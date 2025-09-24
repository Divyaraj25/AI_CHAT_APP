class ChatApp {
  constructor() {
    this.userId = this.getUserId();
    this.currentChatId = null;
    this.isWaitingForResponse = false;
    this.abortController = null;
    this.chatTitleMap = {};
    this.initializeEventListeners();
    this.initializeApp();
  }

  async initializeApp() {
    try {
      await Promise.all([
        this.loadChatHistory(),
        this.loadPromptCategories(),
        this.loadProfile(),
      ]);
    } catch (error) {
      console.error("Error initializing app:", error);
    }
  }

  getUserId() {
    let userId = localStorage.getItem("userId");
    if (!userId) {
      userId = `user_${Math.random().toString(36).slice(2, 11)}`;
      localStorage.setItem("userId", userId);
    }
    return userId;
  }

  initializeEventListeners() {
    // Send message
    document
      .getElementById("send-btn")
      .addEventListener("click", () => this.sendMessage());

    document
      .getElementById("message-input")
      .addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });

    // New chat
    document
      .getElementById("new-chat-btn")
      .addEventListener("click", () => this.newChat());

    // Delete chat
    // document
    //   .getElementById("delete-chat")
    //   .addEventListener("click", () => this.deleteChat());

    // Delete all chats
    document
      .getElementById("delete-all-chats")
      .addEventListener("click", () => this.deleteAllChats());

    // Profile modal
    const profileModal = document.getElementById("profile-modal");

    document
      .querySelector(".close")
      .addEventListener("click", () => this.closeProfileModal());

    window.addEventListener("click", (e) => {
      if (e.target === profileModal) {
        this.closeProfileModal();
      }
    });

    // Profile form
    document.getElementById("profile-form").addEventListener("submit", (e) => {
      e.preventDefault();
      this.saveProfile();
    });

    // Stop generation button
    document
      .getElementById("stop-btn")
      .addEventListener("click", () => this.stopGeneration());

    // Mobile menu toggle
    const menuToggle = document.getElementById("menuToggle");
    menuToggle.addEventListener("click", () => this.toggleSidebar());

    // Profile icon click
    const profileIcon = document.getElementById('profileIcon');
    if (profileIcon) {
      profileIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openProfileModal();
      });
      
      // Make profile icon keyboard accessible
      profileIcon.setAttribute('role', 'button');
      profileIcon.setAttribute('tabindex', '0');
      profileIcon.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.openProfileModal();
        }
      });
    }

    // Close modal when clicking the X
    const closeModal = document.getElementsByClassName("close")[0];
    closeModal.addEventListener("click", () => {
      profileModal.style.display = "none";
      document.body.style.overflow = "";
    });

    // Close modal when clicking outside or pressing Escape
    document.addEventListener('click', (e) => {
      const modal = document.getElementById('profile-modal');
      if (e.target === modal) {
        this.closeProfileModal();
      }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      const modal = document.getElementById('profile-modal');
      if (e.key === 'Escape' && modal.style.display === 'block') {
        this.closeProfileModal();
      }
    });
  }

  toggleInputState(isDisabled) {
    const input = document.getElementById("message-input");
    const sendButton = document.getElementById("send-btn");
    const stopButton = document.getElementById("stop-btn");

    input.disabled = isDisabled;
    sendButton.disabled = isDisabled;

    // Show/hide stop button based on state
    if (isDisabled) {
      sendButton.style.display = "none";
      stopButton.style.display = "flex";
    } else {
      sendButton.style.display = "flex";
      stopButton.style.display = "none";
    }
  }

  async sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();

    if (!message || this.isWaitingForResponse) return;

    input.value = "";
    this.isWaitingForResponse = true;
    this.toggleInputState(true);

    // Create new chat if needed
    if (!this.currentChatId) {
      this.currentChatId = await this.createChat(message);
      await this.loadChatHistory();
    }

    // Add user message to UI
    this.addMessageToUI("user", message);
    this.scrollToBottom();

    // Create assistant message element
    const assistantMessageElement = this.createMessageElement("assistant", "");
    document
      .getElementById("chat-messages")
      .appendChild(assistantMessageElement);
    this.scrollToBottom();

    try {
      await this.streamAssistantResponse(message, assistantMessageElement);
    } catch (error) {
      // Don't show error if the request was aborted intentionally
      if (error.name !== "AbortError") {
        console.error("Error in sendMessage:", error);
        this.showError("Failed to get response. Please try again.");
      }
    } finally {
      this.isWaitingForResponse = false;
      this.toggleInputState(false);
    }
  }

  async streamAssistantResponse(message, messageElement) {
    // Ensure we have a chat ID
    if (!this.currentChatId) {
      this.currentChatId = await this.createChat(message);
    }

    // Create a new AbortController for this request
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    // Flag to track if the request was aborted
    let wasAborted = false;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
        signal, // Pass the signal to the fetch request
        body: JSON.stringify({
          user_id: this.userId,
          chat_id: this.currentChatId,
          message,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, body: ${errorText}`
        );
      }

      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let assistantMessage = "";
      let isProcessing = true;

      // Create a content container for better formatting
      const contentContainer = document.createElement("div");
      contentContainer.className = "assistant-message-content markdown-body";
      messageElement.appendChild(contentContainer);

      // Add loading indicator
      const loadingIndicator = document.createElement("div");
      loadingIndicator.className = "typing-indicator";
      loadingIndicator.innerHTML = "<span></span><span></span><span></span>";

      // Set up abort handler
      signal.addEventListener("abort", () => {
        wasAborted = true;
        // Remove loading indicator
        if (loadingIndicator.parentNode) {
          loadingIndicator.remove();
        }
      });
      contentContainer.appendChild(loadingIndicator);

      const processChunk = async () => {
        try {
          while (isProcessing) {
            const { done, value } = await reader.read();

            if (done) {
              isProcessing = false;
              this.isWaitingForResponse = false;
              // Save the complete message to chat history
              if (this.currentChatId) {
                await this.saveMessageToHistory("assistant", assistantMessage);
              }
              // Remove loading indicator when done
              if (loadingIndicator.parentNode === contentContainer) {
                contentContainer.removeChild(loadingIndicator);
              }
              return;
            }

            // Process the streamed data
            buffer += decoder.decode(value, { stream: true });

            // Split by double newlines to handle multiple events
            const events = buffer.split("\n\n");
            buffer = events.pop() || ""; // Keep incomplete event in buffer

            for (const event of events) {
              if (!event.trim()) continue;

              // Extract data from the event
              const lines = event.split("\n");
              let eventData = "";

              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  const data = line.substring(6).trim();
                  if (data === "[DONE]") {
                    isProcessing = false;
                    this.isWaitingForResponse = false;
                    if (loadingIndicator.parentNode === contentContainer) {
                      contentContainer.removeChild(loadingIndicator);
                    }
                    return;
                  }
                  eventData = data;
                }
              }

              if (!eventData) continue;

              try {
                const parsedData = JSON.parse(eventData);

                // Handle error response
                if (parsedData.error) {
                  console.error("Server error:", parsedData.error);
                  contentContainer.innerHTML = `<div class="error-message">${parsedData.error}</div>`;
                  isProcessing = false;
                  this.isWaitingForResponse = false;
                  return;
                }

                // Handle content chunk
                if (parsedData.content) {
                  assistantMessage += parsedData.content;
                  const formattedMessage = this.formatMessage(assistantMessage);
                  contentContainer.innerHTML = formattedMessage;
                  this.scrollToBottom();
                }

                // Handle done event
                if (parsedData.type === "done") {
                  isProcessing = false;
                  this.isWaitingForResponse = false;
                  if (loadingIndicator.parentNode === contentContainer) {
                    contentContainer.removeChild(loadingIndicator);
                  }
                  return;
                }
              } catch (e) {
                console.error(
                  "Error parsing event data:",
                  e,
                  "Data:",
                  eventData
                );
              }
            }

            // Small delay to prevent UI blocking
            await new Promise((resolve) => setTimeout(resolve, 0));
          }
        } catch (error) {
          // Don't show error if the request was aborted intentionally
          if (error.name === "AbortError") {
            console.log("Request was aborted by user");
            return;
          }
          console.error("Error in processChunk:", error);
          contentContainer.innerHTML =
            '<div class="error-message">Error receiving response. Please try again.</div>';
          throw error;
        }
      };

      await processChunk();
    } catch (error) {
      // Don't show error if the request was aborted intentionally
      if (error.name === "AbortError") {
        console.log("Streaming was aborted by user");
        return;
      }
      console.error("Error in streamAssistantResponse:", error);
      throw error;
    } finally {
      // Clean up the abort controller when done
      if (this.abortController) {
        this.abortController = null;
      }
    }
  }

  addMessageToUI(role, content) {
    const messagesContainer = document.getElementById("chat-messages");
    const messageElement = this.createMessageElement(role, content);
    messagesContainer.appendChild(messageElement);
    this.scrollToBottom();
  }

  formatMessage(text) {
    if (!text) return "";

    // Basic markdown formatting
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
      .replace(/^### (.*$)/gm, "<h3>$1</h3>")
      .replace(/^## (.*$)/gm, "<h2>$1</h2>")
      .replace(/^# (.*$)/gm, "<h1>$1</h1>")
      // Add link formatting with markdown style [text](url)
      .replace(
        /\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
      )
      .replace(/\n/g, "<br>");

    // Handle lists
    formatted = formatted
      .replace(/^\s*[-*+] (.*$)/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");

    return formatted;
  }

  async saveMessageToHistory(role, content) {
    if (!this.currentChatId) return;

    try {
      const response = await fetch(
        `/api/chats/${this.currentChatId}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: this.userId,
            role,
            content,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to save message: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error saving message to history:", error);
      throw error;
    }
  }

  createMessageElement(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}-message`;

    const headerDiv = document.createElement("div");
    headerDiv.className = "message-header";

    const timeSpan = document.createElement("span");
    timeSpan.className = "message-time";
    timeSpan.textContent = new Date().toLocaleTimeString();

    // Create copy button
    const copyButton = document.createElement("button");
    copyButton.className = "copy-btn";
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.setAttribute("aria-label", "Copy message");
    copyButton.title = "Copy to clipboard";

    // Add click event to copy button
    copyButton.addEventListener("click", () => {
      navigator.clipboard
        .writeText(content)
        .then(() => {
          // Show visual feedback
          const originalIcon = copyButton.innerHTML;
          copyButton.innerHTML = '<i class="fas fa-check"></i>';
          copyButton.style.color = "var(--success-color)";

          // Reset after 2 seconds
          setTimeout(() => {
            copyButton.innerHTML = originalIcon;
            copyButton.style.color = "";
          }, 2000);
        })
        .catch((err) => {
          console.error("Failed to copy text: ", err);
        });
    });

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    if (role === "user") {
      contentDiv.textContent = content;
    } else {
      contentDiv.innerHTML = this.formatMessage(content);
    }

    headerDiv.appendChild(timeSpan);
    headerDiv.appendChild(copyButton);
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
  }

  showError(message) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "error-message";
    errorDiv.textContent = message;

    const messagesContainer = document.getElementById("chat-messages");
    messagesContainer.appendChild(errorDiv);
    this.scrollToBottom();
  }

  generateTitleFromMessage(message) {
    // Take first 3 words or 30 characters, whichever comes first
    const words = message.trim().split(/\s+/);
    const shortMessage = words.slice(0, 3).join(" ");
    return shortMessage.length > 30
      ? `${shortMessage.substring(0, 27)}...`
      : shortMessage || "New Chat";
  }

  scrollToBottom() {
    const messagesContainer = document.getElementById("chat-messages");
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async createChat(firstMessage) {
    try {
      // First, create a new chat with a temporary ID
      const tempChatId = `new-chat-${Date.now()}`;
      this.currentChatId = tempChatId;

      // Create the chat in the backend
      const response = await fetch("/api/chats", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: this.userId,
          title:
            firstMessage.substring(0, 30) +
            (firstMessage.length > 30 ? "..." : ""),
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          `Failed to create chat: ${response.status} - ${errorText}`
        );
        return tempChatId; // Return the temp ID if creation fails
      }

      const data = await response.json();

      // If we get a chat_id in the response, use it
      if (data?.chat_id) {
        this.currentChatId = data.chat_id;
        return data.chat_id;
      }

      return tempChatId;
    } catch (error) {
      console.error("Error creating chat:", error);
      // Generate a fallback chat ID if there's an error
      return `new-chat-${Date.now()}`;
    }
  }

  async loadChatHistory() {
    try {
      const response = await fetch(`/api/chats?user_id=${this.userId}`);
      if (!response.ok) throw new Error("Failed to load chat history");

      const chats = await response.json();
      const chatList = document.getElementById("chat-list");
      if (!chatList) return;

      // Store current scroll position
      const scrollPosition = chatList.scrollTop;

      // Create document fragment for better performance
      const fragment = document.createDocumentFragment();

      // Clear existing content
      chatList.innerHTML = "";

      // Add chat history items
      const historyItems = document.createElement("div");
      historyItems.className = "chat-history-items";

      for (const [chatId, chatData] of Object.entries(chats)) {
        const chatItem = document.createElement("div");
        chatItem.className = `chat-item ${
          this.currentChatId === chatId ? "active" : ""
        }`;
        chatItem.dataset.chatId = chatId;

        // Create chat content container
        const chatContent = document.createElement("div");
        chatContent.className = "chat-content";

        // Chat icon
        const icon = document.createElement("i");
        icon.className = "fas fa-comment-alt";

        // Chat title
        const title = document.createElement("span");
        title.className = "chat-title";
        title.textContent = chatData.title || "Untitled Chat";

        // Three-dot menu button
        const menuBtn = document.createElement("button");
        menuBtn.className = "chat-menu-btn";
        menuBtn.innerHTML = '<i class="fas fa-ellipsis-v"></i>';
        menuBtn.setAttribute("aria-label", "Chat options");
        menuBtn.setAttribute("aria-haspopup", "true");
        menuBtn.setAttribute("aria-expanded", "false");

        // Dropdown menu
        const dropdown = document.createElement("div");
        dropdown.className = "chat-dropdown";
        dropdown.setAttribute("role", "menu");
        dropdown.innerHTML = `
          <button class="dropdown-item" data-action="rename" role="menuitem">
            <i class="fas fa-pen"></i> Rename
          </button>
          <button class="dropdown-item" data-action="delete" role="menuitem">
            <i class="fas fa-trash"></i> Delete
          </button>
        `;

        // Toggle dropdown on menu button click only
        menuBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          const isOpen = dropdown.classList.contains("show");

          // Close all other dropdowns
          document.querySelectorAll(".chat-dropdown.show").forEach((d) => {
            if (d !== dropdown) {
              d.classList.remove("show");
              const btn = d.previousElementSibling;
              if (btn) {
                btn.setAttribute("aria-expanded", "false");
              }
            }
          });

          // Toggle current dropdown
          dropdown.classList.toggle("show", !isOpen);
          menuBtn.setAttribute("aria-expanded", !isOpen);
        });

        // Handle dropdown item clicks
        dropdown.querySelectorAll(".dropdown-item").forEach((btn) => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const action = btn.dataset.action;
            dropdown.classList.remove("show");
            menuBtn.setAttribute("aria-expanded", "false");

            if (action === "delete") {
              if (confirm("Are you sure you want to delete this chat?")) {
                this.deleteChat(chatId);
              }
            } else if (action === "rename") {
              this.renameChat(chatId, title);
            }
          });
        });

        // Build the chat item structure
        chatContent.appendChild(icon);
        chatContent.appendChild(title);
        chatItem.appendChild(chatContent);
        chatItem.appendChild(menuBtn);
        chatItem.appendChild(dropdown);

        // Handle chat item click
        chatItem.addEventListener("click", (e) => {
          if (
            !e.target.closest(".chat-menu-btn") &&
            !e.target.closest(".chat-dropdown")
          ) {
            this.loadChat(chatId);
          }
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", (e) => {
          if (
            !chatItem.contains(e.target) &&
            !e.target.closest(".chat-menu-btn")
          ) {
            dropdown.classList.remove("show");
            menuBtn.setAttribute("aria-expanded", "false");
          }
        });

        // Close dropdown on escape key
        document.addEventListener("keydown", (e) => {
          if (e.key === "Escape" && dropdown.classList.contains("show")) {
            dropdown.classList.remove("show");
            menuBtn.setAttribute("aria-expanded", "false");
            menuBtn.focus();
          }
        });

        historyItems.appendChild(chatItem);
      }

      fragment.appendChild(historyItems);
      chatList.appendChild(fragment);

      // Restore scroll position
      chatList.scrollTop = scrollPosition;
    } catch (error) {
      console.error("Error loading chat history:", error);
      this.showError("Failed to load chat history. Please try again.");
    }
  }

  async loadChat(chatId) {
    try {
      const response = await fetch(`/api/chats?user_id=${this.userId}`);
      const chats = await response.json();
      const chat = chats[chatId];

      if (!chat) return;

      this.currentChatId = chatId;

      // Update UI
      document.getElementById("current-chat-title").textContent =
        chat.title || "Untitled Chat";

      const messagesContainer = document.getElementById("chat-messages");
      messagesContainer.innerHTML = "";

      // Add messages to UI
      chat.messages.forEach((message) => {
        this.addMessageToUI(message.role, message.content);
      });

      this.scrollToBottom();

      // Update active chat in sidebar
      document.querySelectorAll(".chat-item").forEach((item) => {
        item.classList.remove("active");
      });
      document
        .querySelector(`.chat-item[data-chat-id="${chatId}"]`)
        .classList.add("active");

      // Hide welcome message and show prompt suggestions
      const welcomeMessage = document.querySelector(".welcome-message");
      if (welcomeMessage) {
        welcomeMessage.style.display = "none";
      }
    } catch (error) {
      console.error("Error loading chat:", error);
    }
  }

  async deleteChat(chatId = null) {
    const targetChatId = chatId || this.currentChatId;
    if (!targetChatId) return;

    if (!confirm("Are you sure you want to delete this chat?")) return;

    try {
      const response = await fetch(
        `/api/chats/${targetChatId}?user_id=${this.userId}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        // If we're deleting the current chat, create a new one
        if (targetChatId === this.currentChatId) {
          this.newChat();
        }
        await this.loadChatHistory();
      }
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  }

  async deleteAllChats() {
    if (
      !confirm(
        "Are you sure you want to delete ALL chats? This cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`/api/chats?user_id=${this.userId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        this.newChat();
        this.loadChatHistory();
      }
    } catch (error) {
      console.error("Error deleting all chats:", error);
    }
  }

  newChat() {
    this.currentChatId = null;
    document.getElementById("current-chat-title").textContent = "New Chat";

    const messagesContainer = document.getElementById("chat-messages");
    messagesContainer.innerHTML = "";

    // Show welcome message
    const welcomeMessage = document.querySelector(".welcome-message");
    if (welcomeMessage) {
      welcomeMessage.style.display = "block";
    }

    // Clear active chat in sidebar
    document.querySelectorAll(".chat-item").forEach((item) => {
      item.classList.remove("active");
    });
  }

  async loadPromptCategories() {
    try {
      const response = await fetch("/api/prompts/categories");
      const categories = await response.json();

      const categoriesContainer = document.getElementById("prompt-categories");
      categoriesContainer.innerHTML = "";

      for (const category of categories) {
        const categoryBtn = document.createElement("button");
        categoryBtn.className = "category-btn";
        categoryBtn.innerHTML = `
          <i class="fas fa-${this.getCategoryIcon(category)}"></i>
          <span>${this.formatCategoryName(category)}</span>
        `;

        categoryBtn.addEventListener("click", () => {
          this.loadPromptsForCategory(category);
        });

        categoriesContainer.appendChild(categoryBtn);
      }
    } catch (error) {
      console.error("Error loading prompt categories:", error);
    }
  }

  getCategoryIcon(category) {
    const icons = {
      daily_life: "calendar-day",
      personal_trainee: "dumbbell",
      meal_planner: "utensils",
      recipe_khazana: "book",
      gate_preparation: "graduation-cap",
      qna: "question-circle",
    };
    return icons[category] || "lightbulb";
  }

  formatCategoryName(category) {
    return category
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  async loadPromptsForCategory(category) {
    try {
      const response = await fetch(`/api/prompts?category=${category}`);
      const prompts = await response.json();

      const suggestionsContainer =
        document.getElementById("prompt-suggestions");
      suggestionsContainer.innerHTML = "";

      for (const prompt of prompts) {
        const suggestion = document.createElement("div");
        suggestion.className = "prompt-suggestion";
        suggestion.textContent = prompt;

        suggestion.addEventListener("click", () => {
          document.getElementById("message-input").value = prompt;
          document.getElementById("send-btn").click();
        });

        suggestionsContainer.appendChild(suggestion);
      }

      // Hide welcome message
      const welcomeMessage = document.querySelector(".welcome-message");
      if (welcomeMessage) {
        welcomeMessage.style.display = "none";
      }
    } catch (error) {
      console.error("Error loading prompts:", error);
    }
  }

  openProfileModal() {
    const modal = document.getElementById('profile-modal');
    const sidebar = document.getElementById('sidebar');
    
    // Close sidebar if open
    if (sidebar.classList.contains('active')) {
      this.toggleSidebar();
    }
    
    // Open modal
    modal.style.display = 'block';
    document.body.classList.add('modal-open');
    document.body.style.overflow = 'hidden';
    
    // Focus on first input for better accessibility
    const firstInput = modal.querySelector('input, button, [tabindex]');
    if (firstInput) {
      firstInput.focus();
    }
  }

  closeProfileModal() {
    document.getElementById("profile-modal").style.display = "none";
  }

  async loadProfile() {
    try {
      const response = await fetch(`/api/profile?user_id=${this.userId}`);
      const profile = await response.json();

      if (profile && Object.keys(profile).length > 0) {
        // Helper function to safely set values
        const setValueIfExists = (elementId, value) => {
          const element = document.getElementById(elementId);
          if (element) {
            element.value = value || "";
          }
        };

        // Helper function to set select value
        const setSelectValue = (elementId, value, defaultValue = "") => {
          const element = document.getElementById(elementId);
          if (!element) return;

          const option = Array.from(element.options).find(
            (opt) => opt.value === (value || defaultValue)
          );
          if (option) option.selected = true;
        };

        // Fill form fields
        setValueIfExists("name", profile.name || "");
        setValueIfExists("age", profile.age || "");

        // Handle select fields
        setSelectValue("dietary_preferences", profile.dietary_preferences);
        setSelectValue("fitness_level", profile.fitness_level);
        setSelectValue("ai_tone", profile.ai_tone, "professional");

        // Handle goals (array)
        if (Array.isArray(profile.goals)) {
          setValueIfExists("goals", profile.goals.join(", "));
        } else if (typeof profile.goals === "string") {
          setValueIfExists("goals", profile.goals);
        }

        // Handle interests (array)
        if (Array.isArray(profile.interests)) {
          setValueIfExists("interests", profile.interests.join("\n"));
        } else if (typeof profile.interests === "string") {
          const interests = profile.interests
            .split(",")
            .map((i) => i.trim())
            .filter((i) => i);
          setValueIfExists("interests", interests.join("\n"));
        }
      }
    } catch (error) {
      console.error("Error loading profile:", error);
      this.showError("Failed to load profile. Please try again.");
    }
  }

  async saveProfile() {
    // Get form values
    const name = document.getElementById("name").value.trim();
    const age = document.getElementById("age").value.trim();
    const dietary_preferences = document.getElementById(
      "dietary_preferences"
    ).value;
    const fitness_level = document.getElementById("fitness_level").value;
    const ai_tone = document.getElementById("ai_tone").value;

    // Process goals (comma-separated)
    const goals = document
      .getElementById("goals")
      .value.split(",")
      .map((g) => g.trim())
      .filter((g) => g);

    // Process interests (newline-separated)
    const interests = document
      .getElementById("interests")
      .value.split("\n")
      .map((i) => i.trim())
      .filter((i) => i);

    // Validate required fields
    if (
      !name ||
      !age ||
      !dietary_preferences ||
      !fitness_level ||
      !ai_tone ||
      goals.length === 0 ||
      interests.length === 0
    ) {
      this.showError("Please fill in all required fields.");
      return;
    }

    const formData = {
      name,
      age,
      goals,
      dietary_preferences,
      fitness_level,
      interests,
      ai_tone,
    };

    try {
      // Check if profile exists
      const profileResponse = await fetch(
        `/api/profile?user_id=${this.userId}`
      );
      const existingProfile = await profileResponse.json();

      let response;
      if (existingProfile && Object.keys(existingProfile).length > 0) {
        // Update existing profile
        response = await fetch(`/api/profile?user_id=${this.userId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });
      } else {
        // Create new profile
        response = await fetch(`/api/profile?user_id=${this.userId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });
      }

      if (response.ok) {
        alert("Profile saved successfully!");
        this.closeProfileModal();
      } else {
        throw new Error("Failed to save profile");
      }
    } catch (error) {
      console.error("Error saving profile:", error);
      alert("Error saving profile. Please try again.");
    }
  }

  stopGeneration() {
    // Only proceed if we have an active request and we're not already aborted
    if (this.abortController) {
      try {
        // Store a reference to the current controller
        const controller = this.abortController;
        this.abortController = null; // Clear it first to prevent multiple abort calls

        // Abort the request
        controller.abort();

        // Show a message indicating the generation was stopped
        const messagesContainer = document.getElementById("chat-messages");
        const stopMessage = document.createElement("div");
        stopMessage.className = "info-message";
        stopMessage.textContent = "Response generation was stopped.";
        messagesContainer.appendChild(stopMessage);
        this.scrollToBottom();
      } catch (error) {
        console.error("Error stopping generation:", error);
      } finally {
        this.abortController = null;
        this.isWaitingForResponse = false;
        this.toggleInputState(false);
      }
    }
  }

  async renameChat(chatId, titleElement) {
    const currentTitle = titleElement.textContent;

    try {
      // Use a more robust prompt implementation
      const newTitle = window.prompt("Enter new chat title:", currentTitle);

      if (!newTitle || newTitle.trim() === "" || newTitle === currentTitle) {
        return; // No change or empty title
      }

      const trimmedTitle = newTitle.trim();

      // Show loading state
      titleElement.textContent = "Updating...";

      const response = await fetch(`/api/chats/${chatId}/title`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: this.userId,
          title: trimmedTitle,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || "Failed to update chat title");
      }

      // Update the title in the UI
      titleElement.textContent = trimmedTitle;

      // Update the title in the chatTitleMap if it exists
      if (this.chatTitleMap[chatId]) {
        this.chatTitleMap[chatId] = trimmedTitle;
      }

      // Show success message
      if (this.showToast) {
        this.showToast("Chat title updated successfully");
      } else {
        console.log("Chat title updated successfully");
      }

      return true; // Indicate success
    } catch (error) {
      console.error("Error updating chat title:", error);
      // Revert to original title on error
      titleElement.textContent = currentTitle;

      // Show error message
      if (this.showError) {
        this.showError(
          "Failed to update chat title: " + (error.message || "Unknown error")
        );
      } else {
        console.error(
          "Failed to update chat title:",
          error.message || "Unknown error"
        );
      }

      return false; // Indicate failure
    }
  }

  toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const isOpening = !sidebar.classList.contains('active');
    
    // Close profile modal if open
    if (isOpening) {
      this.closeProfileModal();
    }
    
    // Toggle sidebar
    sidebar.classList.toggle('active', isOpening);
    overlay.classList.toggle('active', isOpening);
    
    // Toggle body class for disabling interactions
    if (isOpening) {
      document.body.classList.add('sidebar-open');
      document.body.style.overflow = 'hidden';
    } else {
      document.body.classList.remove('sidebar-open');
      document.body.style.overflow = '';
    }
  }
}

// Initialize the app when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const app = new ChatApp();
  window.app = app; // Make app accessible from console for debugging
});
