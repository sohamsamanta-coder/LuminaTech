"use strict";

// ================= PAGE ELEMENTS =================

const searchInput = document.getElementById("productSearch");
const topSearchInput = document.getElementById("topSearch");
const topSearchButton = document.getElementById("topSearchBtn");
const categoryFilter = document.getElementById("categoryFilter");
const searchButton = document.getElementById("searchBtn");
const emptyMessage = document.getElementById("emptyMessage");
const cartCount = document.getElementById("cartCount");
const cartLink = document.getElementById("cartLink");
const loginLink = document.getElementById("loginLink");
const registerLink = document.getElementById("registerLink");

const productCards = Array.from(document.querySelectorAll(".product-card"));
const categoryLinks = Array.from(document.querySelectorAll(".category-bar a[data-category]"));
const addButtons = Array.from(document.querySelectorAll(".add-button"));

const CART_STORAGE_KEY = "luminaTechCart";
let cart = loadCart();


// ================= CART STORAGE =================

function loadCart() {
    try {
        const savedCart = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
        return new Set(Array.isArray(savedCart) ? savedCart.map(String) : []);
    } catch (error) {
        console.warn("Could not read the saved cart.", error);
        return new Set();
    }
}


function saveCart() {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify([...cart]));
    } catch (error) {
        console.warn("Could not save the cart.", error);
    }
}


function updateCartCount() {
    if (cartCount) {
        cartCount.textContent = String(cart.size);
    }
}


function updateCartButtons() {
    addButtons.forEach(function (button) {
        const card = button.closest(".product-card");
        const productId = card ? String(card.dataset.productId) : "";
        const isAdded = cart.has(productId);

        button.classList.toggle("added", isAdded);
        button.textContent = isAdded ? "✓ Added to Cart" : "🛒 Add to Cart";
        button.setAttribute("aria-pressed", String(isAdded));
    });
}


// ================= PRODUCT FILTERING =================

function updateActiveCategory() {
    const selectedCategory = categoryFilter ? categoryFilter.value.toLowerCase().trim() : "";

    categoryLinks.forEach(function (link) {
        const linkCategory = (link.dataset.category || "").toLowerCase().trim();
        link.classList.toggle("active", selectedCategory !== "" && linkCategory === selectedCategory);
    });
}


function filterProducts() {
    if (!searchInput || !categoryFilter) {
        return;
    }

    const searchText = searchInput.value.toLowerCase().trim();
    const selectedCategory = categoryFilter.value.toLowerCase().trim();

    let visibleProducts = 0;

    productCards.forEach(function (card) {
        const productName = (card.dataset.name || "").toLowerCase();
        const productCategory = (card.dataset.category || "").toLowerCase();

        const textMatches =
            searchText === "" ||
            productName.includes(searchText) ||
            productCategory.includes(searchText);

        const categoryMatches =
            selectedCategory === "" ||
            productCategory === selectedCategory;

        const shouldShow = textMatches && categoryMatches;
        card.hidden = !shouldShow;

        if (shouldShow) {
            visibleProducts += 1;
        }
    });

    if (emptyMessage) {
        emptyMessage.hidden = visibleProducts !== 0;
    }

    updateActiveCategory();
}


// ================= SEARCH =================

function copyTopSearchAndFilter() {
    if (!topSearchInput || !searchInput) {
        return;
    }

    searchInput.value = topSearchInput.value;
    filterProducts();
    document.getElementById("products")?.scrollIntoView({ behavior: "smooth" });
}


if (searchButton) {
    searchButton.addEventListener("click", filterProducts);
}

if (topSearchButton) {
    topSearchButton.addEventListener("click", copyTopSearchAndFilter);
}

if (searchInput) {
    searchInput.addEventListener("input", filterProducts);
    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            filterProducts();
        }
    });
}

if (topSearchInput) {
    topSearchInput.addEventListener("input", function () {
        if (searchInput) {
            searchInput.value = topSearchInput.value;
        }
        filterProducts();
    });

    topSearchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            copyTopSearchAndFilter();
        }
    });
}


// ================= CATEGORY FILTER =================

if (categoryFilter) {
    categoryFilter.addEventListener("change", filterProducts);
}


categoryLinks.forEach(function (link) {
    link.addEventListener("click", function () {
        const categoryName = link.dataset.category || "";

        if (categoryFilter) {
            categoryFilter.value = categoryName;
        }

        if (searchInput) {
            searchInput.value = "";
        }

        if (topSearchInput) {
            topSearchInput.value = "";
        }

        filterProducts();
    });
});


// Keep these functions available if another page or inline HTML uses them.
function searchFromTop() {
    copyTopSearchAndFilter();
}

function selectCategory(categoryName) {
    if (categoryFilter) {
        categoryFilter.value = categoryName;
    }

    if (searchInput) {
        searchInput.value = "";
    }

    if (topSearchInput) {
        topSearchInput.value = "";
    }

    filterProducts();
}

window.searchFromTop = searchFromTop;
window.selectCategory = selectCategory;


// ================= ADD TO CART =================

addButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const card = button.closest(".product-card");

        if (!card) {
            return;
        }

        const productId = String(card.dataset.productId || "");

        if (!productId) {
            return;
        }

        if (cart.has(productId)) {
            cart.delete(productId);
        } else {
            cart.add(productId);
        }

        saveCart();
        updateCartCount();
        updateCartButtons();
    });
});


// ================= FRONT-END DEMO LINKS =================

function preventDemoLink(event) {
    event.preventDefault();
    alert("Login and registration will be added to the Django authentication system next.");
}

if (loginLink) {
    loginLink.addEventListener("click", preventDemoLink);
}

if (registerLink) {
    registerLink.addEventListener("click", preventDemoLink);
}

if (cartLink) {
    cartLink.addEventListener("click", function (event) {
        event.preventDefault();
        alert(`Your cart currently contains ${cart.size} product${cart.size === 1 ? "" : "s"}.`);
    });
}


// ================= INITIAL STATE =================

updateCartCount();
updateCartButtons();
filterProducts();

// LUMINA AI CHATBOT

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

if (chatForm) {

    chatForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        // Show user message
        const userMessage = document.createElement("div");

        userMessage.className = "user-message";
        userMessage.textContent = message;

        chatMessages.appendChild(userMessage);

        // Clear input
        chatInput.value = "";

        // Show loading message
        const botMessage = document.createElement("div");

        botMessage.className = "bot-message";
        botMessage.textContent = "Thinking...";

        chatMessages.appendChild(botMessage);

        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {

            const formData = new FormData(chatForm);

            formData.set("message", message);

            const response = await fetch("/chatbot/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.reply || "Request failed");
            }

            botMessage.textContent =
                data.reply || "No response received.";

        } catch (error) {

            console.error("Lumina error:", error);

            botMessage.textContent =
                "Sorry, Lumina could not connect to the AI service.";
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;

    });

}

// LUMINA CHAT WINDOW

const luminaButton = document.getElementById("luminaButton");
const luminaChat = document.getElementById("luminaChat");
const luminaClose = document.getElementById("luminaClose");


// Open / Close Lumina

if (luminaButton && luminaChat) {

    luminaButton.addEventListener("click", function () {

        luminaChat.classList.toggle("open");

    });

}


// Close button

if (luminaClose && luminaChat) {

    luminaClose.addEventListener("click", function () {

        luminaChat.classList.remove("open");

    });

}
document.querySelectorAll(".product-card").forEach((card) => {
    card.addEventListener("click", (event) => {
        if (event.target.closest("button, a, input, select")) {
            return;
        }

        const productId = card.dataset.productId;

        if (productId) {
            window.location.href = `/product/${productId}/`;
        }
    });
});