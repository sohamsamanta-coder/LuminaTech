
"use strict";

// ================= PAGE ELEMENTS =================

const searchInput = document.getElementById("productSearch");
const topSearchInput = document.getElementById("topSearch");
const topSearchButton = document.getElementById("topSearchBtn");
const categoryFilter = document.getElementById("categoryFilter");
const searchButton = document.getElementById("searchBtn");
const cartCount = document.getElementById("cartCount");
const cartLink = document.getElementById("cartLink");
const loginLink = document.getElementById("loginLink");
const registerLink = document.getElementById("registerLink");

const productFilterForm = document.getElementById("productFilterForm");

const productCards = Array.from(
    document.querySelectorAll(".product-card")
);

const categoryLinks = Array.from(
    document.querySelectorAll(".category-bar a[data-category]")
);

const addButtons = Array.from(
    document.querySelectorAll(".add-button")
);


// ================= DATABASE CART STORAGE =================

const CART_STATE_URL = "/cart/state/";
const CART_ADD_URL = "/cart/add/";

let cart = new Map();
let cartCountTotal = 0;


// ================= CSRF TOKEN =================

function getCsrfToken() {

    const cookie = document.cookie.match(
        /(?:^|;\s*)csrftoken=([^;]+)/
    );

    if (cookie) {
        return decodeURIComponent(cookie[1]);
    }

    const inputToken = document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    const metaToken = document.querySelector(
        'meta[name="csrf-token"]'
    );

    return inputToken?.value || metaToken?.content || "";
}


// ================= CART STATE =================

// Update the cart using data received from Django

function updateCartFromServer(data) {

    const items = Array.isArray(data.items) ? data.items : [];

    cart = new Map(
        items.map(item => [
            String(item.id),
            Math.max(1, parseInt(item.quantity, 10) || 1)
        ])
    );

    cartCountTotal = parseInt(data.cart_count, 10) || 0;

    updateCartCount();
    updateCartButtons();
}


// Update navbar cart badge

function updateCartCount() {

    if (!cartCount) {
        return;
    }

    cartCount.textContent = String(cartCountTotal);
    cartCount.hidden = cartCountTotal === 0;
}


// Update Add to Cart button appearance

function updateCartButtons() {

    addButtons.forEach(function (button) {

        const card = button.closest(".product-card");

        const productId = String(
            card?.dataset.productId || button.dataset.productId || ""
        );

        const isAdded = cart.has(productId);

        button.classList.toggle("added", isAdded);

        button.innerHTML = isAdded
            ? '<i class="fa-solid fa-check" aria-hidden="true"></i> Added to Cart'
            : '<i class="fa-solid fa-plus" aria-hidden="true"></i> Add to Cart';

        button.setAttribute("aria-pressed", String(isAdded));

    });

}


// Fetch the current cart from Django

async function loadCartFromServer() {

    try {

        const response = await fetch(CART_STATE_URL, {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Could not load cart.");
        }

        const data = await response.json();

        updateCartFromServer(data);

    } catch (error) {

        console.error("Cart loading error:", error);

    }

}


// Send cart changes to Django

async function sendCartRequest(url, payload) {

    const csrfToken = getCsrfToken();

    if (!csrfToken) {

        throw new Error(
            "Django CSRF token not found. Please check the CSRF setup."
        );

    }

    const response = await fetch(url, {

        method: "POST",

        credentials: "same-origin",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },

        body: JSON.stringify(payload)

    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {

        throw new Error(
            data.error || "Unable to update your cart."
        );

    }

    updateCartFromServer(data);

    return data;

}


// ================= SERVER-SIDE PRODUCT FILTERING =================

// Update active category navigation link

function updateActiveCategory() {

    const selectedCategory = categoryFilter
        ? categoryFilter.value.toLowerCase().trim()
        : "";

    categoryLinks.forEach(function (link) {

        const linkCategory = (
            link.dataset.category || ""
        ).toLowerCase().trim();

        link.classList.toggle(
            "active",
            selectedCategory !== "" &&
            linkCategory === selectedCategory
        );

    });

}


// Submit category and search filters to Django

function submitProductFilters() {

    if (productFilterForm) {

        productFilterForm.requestSubmit();

    }

}


// ================= SEARCH =================

// Copy navbar search into the main search form
// Django handles the actual search.

function copyTopSearchAndFilter(event) {

    if (event) {
        event.preventDefault();
    }

    const searchText = topSearchInput
        ? topSearchInput.value.trim()
        : "";

    if (searchInput && productFilterForm) {

        searchInput.value = searchText;

        submitProductFilters();

    } else {

        // When searching from another page, go to the home page.

        window.location.href =
            `/?q=${encodeURIComponent(searchText)}#products`;

    }

}


// Main search form

if (productFilterForm) {

    productFilterForm.addEventListener("submit", function () {

        // Allow the browser to submit the GET form normally.

    });

}


// Navbar search button

if (topSearchButton) {

    topSearchButton.addEventListener(
        "click",
        copyTopSearchAndFilter
    );

}


// Keep navbar search and main search synchronized

if (topSearchInput) {

    topSearchInput.addEventListener("input", function () {

        if (searchInput) {

            searchInput.value = topSearchInput.value;

        }

    });


    topSearchInput.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            copyTopSearchAndFilter();

        }

    });

}


// ================= CATEGORY FILTER =================

// Submit automatically when category changes

if (categoryFilter && productFilterForm) {

    categoryFilter.addEventListener("change", function () {

        submitProductFilters();

    });

}


// Category navigation links

categoryLinks.forEach(function (link) {

    link.addEventListener("click", function (event) {

        if (!categoryFilter || !productFilterForm) {

            // If the user is on another page, navigate to
            // the home page with the selected category.

            const categoryName = link.dataset.category || "";

            event.preventDefault();

            window.location.href =
                `/?category=${encodeURIComponent(categoryName)}#products`;

            return;

        }

        event.preventDefault();

        const categoryName = link.dataset.category || "";

        categoryFilter.value = categoryName;

        if (searchInput) {
            searchInput.value = "";
        }

        if (topSearchInput) {
            topSearchInput.value = "";
        }

        submitProductFilters();

    });

});


// Keep these functions available for existing HTML

function searchFromTop() {

    copyTopSearchAndFilter();

}


function selectCategory(categoryName) {

    if (categoryFilter && productFilterForm) {

        categoryFilter.value = categoryName;

        if (searchInput) {
            searchInput.value = "";
        }

        if (topSearchInput) {
            topSearchInput.value = "";
        }

        submitProductFilters();

    } else {

        window.location.href =
            `/?category=${encodeURIComponent(categoryName)}#products`;

    }

}


window.searchFromTop = searchFromTop;
window.selectCategory = selectCategory;


// Highlight the selected category on page load

updateActiveCategory();


// ================= ADD TO CART =================

addButtons.forEach(function (button) {

    button.addEventListener("click", async function () {

        const card = button.closest(".product-card");

        const productId = String(
            card?.dataset.productId || button.dataset.productId || ""
        );

        if (!productId || button.disabled) {
            return;
        }

        button.disabled = true;

        try {

            await sendCartRequest(CART_ADD_URL, {

                product_id: parseInt(productId, 10),
                quantity: 1

            });

        } catch (error) {

            console.error("Add to Cart error:", error);

            alert(error.message);

        } finally {

            button.disabled = false;

            updateCartButtons();

        }

    });

});


// ================= INITIAL STATE =================

updateCartCount();
updateCartButtons();
loadCartFromServer();


// ================= LUMINA AI CHATBOT =================

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

            const reply = data.reply || "No response received.";

            if (window.marked && window.DOMPurify) {

                botMessage.innerHTML = window.DOMPurify.sanitize(
                    window.marked.parse(reply)
                );

            } else {

                botMessage.textContent = reply;

            }

        } catch (error) {

            console.error("Lumina error:", error);

            botMessage.textContent =
                "Sorry, Lumina could not connect to the AI service.";

        }

        chatMessages.scrollTop = chatMessages.scrollHeight;

    });

}


// ================= LUMINA CHAT WINDOW =================

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


// ================= PRODUCT CARD NAVIGATION =================

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


// ================= MOBILE HAMBURGER MENU =================

const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const userLinks = document.getElementById("userLinks");

if (mobileMenuBtn && userLinks) {

    mobileMenuBtn.addEventListener("click", function () {

        const isOpen = userLinks.classList.toggle("is-open");

        mobileMenuBtn.classList.toggle("is-open", isOpen);

        mobileMenuBtn.setAttribute(
            "aria-expanded",
            String(isOpen)
        );

        mobileMenuBtn.setAttribute(
            "aria-label",
            isOpen ? "Close navigation menu" : "Open navigation menu"
        );

    });


    // Close menu after clicking a navigation link

    userLinks.querySelectorAll("a").forEach(function (link) {

        link.addEventListener("click", function () {

            userLinks.classList.remove("is-open");

            mobileMenuBtn.classList.remove("is-open");

            mobileMenuBtn.setAttribute("aria-expanded", "false");

        });

    });


    // Close menu using Escape

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            userLinks.classList.remove("is-open");

            mobileMenuBtn.classList.remove("is-open");

            mobileMenuBtn.setAttribute("aria-expanded", "false");

        }

    });

}
