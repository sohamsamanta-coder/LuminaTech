
(function () {
    "use strict";

    // ================= PAGE ELEMENTS =================

    const CART_STATE_URL = "/cart/state/";
    const CART_UPDATE_URL = "/cart/update/";
    const CART_REMOVE_URL = "/cart/remove/";

    const cartItems = document.getElementById("cartItems");
    const emptyState = document.getElementById("cartEmptyState");
    const checkoutButton = document.getElementById("checkoutButton");

    // Run this script only on the cart page.
    if (!cartItems) {
        return;
    }

    let cart = new Map();
    let cartSubtotal = 0;
    let promoApplied = false;
    let requestInProgress = false;


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


    // ================= PRICE FORMATTING =================

    function formatPrice(amount) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(amount);
    }


    // ================= CART STATE =================

    function updateCartFromServer(data) {
        const items = Array.isArray(data.items)
            ? data.items
            : [];

        cart = new Map(
            items.map(function (product) {
                return [
                    String(product.id),
                    {
                        ...product,
                        price: Number(product.price) || 0,
                        quantity: Math.max(
                            1,
                            parseInt(product.quantity, 10) || 1
                        )
                    }
                ];
            })
        );

        cartSubtotal = Number(data.subtotal) || 0;

        updateCartCount(data.cart_count);
        renderCart();
    }


    // ================= NAVBAR CART COUNT =================

    function updateCartCount(count) {
        const headerCount = document.getElementById("cartCount");

        if (!headerCount) {
            return;
        }

        const totalQuantity = parseInt(count, 10) || 0;

        headerCount.textContent = String(totalQuantity);
        headerCount.hidden = totalQuantity === 0;
    }


    // ================= LOAD CART FROM DJANGO =================

    async function loadCart() {
        try {
            const response = await fetch(CART_STATE_URL, {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error("Could not load your cart.");
            }

            const data = await response.json();

            updateCartFromServer(data);

        } catch (error) {
            console.error("Cart loading error:", error);
            alert("Unable to load your cart. Please refresh the page.");
        }
    }


    // ================= SEND CART REQUEST =================

    async function sendCartRequest(url, payload) {
        const csrfToken = getCsrfToken();

        if (!csrfToken) {
            throw new Error("CSRF token not found. Please refresh the page.");
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


    // ================= CREATE CART PRODUCT =================

    function createCartItem(product) {
        const item = document.createElement("article");

        item.className = "cart-item";
        item.dataset.productId = product.id;


        // Product image
        const imageBox = document.createElement("div");
        imageBox.className = "cart-item-image";

        const image = document.createElement("img");

        image.alt = product.name;

        if (product.image) {
            image.src = product.image;
        } else {
            imageBox.hidden = true;
        }

        imageBox.appendChild(image);


        // Product information
        const information = document.createElement("div");
        information.className = "cart-item-info";

        const category = document.createElement("p");
        category.className = "cart-item-category";
        category.textContent = product.category;

        const name = document.createElement("h3");
        name.textContent = product.name;

        const price = document.createElement("p");
        price.className = "cart-item-price";
        price.textContent = formatPrice(product.price);

        const lineTotal = document.createElement("p");
        lineTotal.className = "cart-item-line-total";

        lineTotal.textContent =
            formatPrice(product.price * product.quantity) + " total";

        information.append(
            category,
            name,
            price,
            lineTotal
        );


        // Quantity and remove controls
        const actions = document.createElement("div");
        actions.className = "cart-item-actions";

        const removeButton = document.createElement("button");

        removeButton.type = "button";
        removeButton.className = "cart-remove-button";
        removeButton.dataset.cartAction = "remove";

        removeButton.setAttribute(
            "aria-label",
            "Remove " + product.name
        );

        removeButton.innerHTML =
            '<i class="fa-solid fa-trash-can"></i>';


        // Quantity controls
        const quantityControl = document.createElement("div");
        quantityControl.className = "quantity-control";

        const decreaseButton = document.createElement("button");

        decreaseButton.type = "button";
        decreaseButton.dataset.cartAction = "decrease";

        decreaseButton.setAttribute(
            "aria-label",
            "Decrease quantity"
        );

        decreaseButton.innerHTML =
            '<i class="fa-solid fa-minus"></i>';


        const quantityNumber = document.createElement("span");

        quantityNumber.className = "quantity-number";
        quantityNumber.textContent = product.quantity;


        const increaseButton = document.createElement("button");

        increaseButton.type = "button";
        increaseButton.dataset.cartAction = "increase";

        increaseButton.setAttribute(
            "aria-label",
            "Increase quantity"
        );

        increaseButton.innerHTML =
            '<i class="fa-solid fa-plus"></i>';


        quantityControl.append(
            decreaseButton,
            quantityNumber,
            increaseButton
        );

        actions.append(
            removeButton,
            quantityControl
        );

        item.append(
            imageBox,
            information,
            actions
        );

        return item;
    }


    // ================= ORDER SUMMARY =================

    function updateSummary() {
        const subtotal = cartSubtotal;

        // Demonstration delivery rule:
        // Free delivery for orders of ₹10,000 or more.
        const deliveryFee =
            subtotal === 0 || subtotal >= 10000
                ? 0
                : 99;

        // Demonstration coupon:
        // LUMINA10 provides a 10% discount.
        const discount = promoApplied
            ? Math.round(subtotal * 0.10)
            : 0;

        const total = subtotal + deliveryFee - discount;

        const subtotalElement =
            document.getElementById("cartSubtotal");

        const deliveryElement =
            document.getElementById("cartDelivery");

        const discountElement =
            document.getElementById("cartDiscount");

        const totalElement =
            document.getElementById("cartTotal");

        const discountRow =
            document.getElementById("cartDiscountRow");


        if (subtotalElement) {
            subtotalElement.textContent = formatPrice(subtotal);
        }

        if (deliveryElement) {
            deliveryElement.textContent =
                deliveryFee === 0
                    ? "FREE"
                    : formatPrice(deliveryFee);
        }

        if (discountElement) {
            discountElement.textContent =
                "-" + formatPrice(discount);
        }

        if (totalElement) {
            totalElement.textContent = formatPrice(total);
        }

        if (discountRow) {
            discountRow.hidden =
                !promoApplied || subtotal === 0;
        }
    }


    // ================= RENDER CART =================

    function renderCart() {
        cartItems.replaceChildren();

        let totalQuantity = 0;

        cart.forEach(function (product) {
            totalQuantity += product.quantity;

            cartItems.appendChild(
                createCartItem(product)
            );
        });


        // Update cart heading
        const itemLabel =
            totalQuantity === 1 ? "item" : "items";

        const headingCount =
            document.getElementById("cart-heading-count");

        const itemsCount =
            document.getElementById("cart-items-count");

        if (headingCount) {
            headingCount.textContent =
                totalQuantity + " " + itemLabel;
        }

        if (itemsCount) {
            itemsCount.textContent =
                totalQuantity + " " + itemLabel;
        }


        // Show or hide empty cart message
        if (emptyState) {
            emptyState.hidden = totalQuantity !== 0;
        }


        // Update order summary
        updateSummary();


        // Disable checkout when the cart is empty.
        if (checkoutButton) {
            checkoutButton.disabled = totalQuantity === 0;
        }
    }


    // ================= QUANTITY AND REMOVE ACTIONS =================

    cartItems.addEventListener("click", async function (event) {
        const button = event.target.closest(
            "button[data-cart-action]"
        );

        if (!button || requestInProgress) {
            return;
        }

        const item = button.closest(".cart-item");

        if (!item) {
            return;
        }

        const productId = item.dataset.productId;

        const action = button.dataset.cartAction;

        const product = cart.get(productId);

        if (!product) {
            return;
        }


        let url;
        let payload;


        if (action === "increase") {
            url = CART_UPDATE_URL;

            payload = {
                product_id: Number(productId),
                quantity: product.quantity + 1
            };

        } else if (action === "decrease") {

            // Minimum quantity is 1.
            if (product.quantity <= 1) {
                return;
            }

            url = CART_UPDATE_URL;

            payload = {
                product_id: Number(productId),
                quantity: product.quantity - 1
            };

        } else if (action === "remove") {

            url = CART_REMOVE_URL;

            payload = {
                product_id: Number(productId)
            };

        } else {
            return;
        }


        requestInProgress = true;

        // Prevent multiple cart requests at the same time.
        cartItems.querySelectorAll("button").forEach(function (btn) {
            btn.disabled = true;
        });

        try {
            await sendCartRequest(url, payload);

        } catch (error) {
            console.error("Cart update error:", error);
            alert(error.message);

        } finally {
            requestInProgress = false;

            // Rebuild the cart using the latest available data.
            renderCart();
        }
    });


    // ================= PROMO CODE =================

    const applyPromo = document.getElementById("applyPromo");
    const promoInput = document.getElementById("promoCode");
    const promoMessage = document.getElementById("promoMessage");

    if (applyPromo) {
        applyPromo.addEventListener("click", function () {

            const code = promoInput
                ? promoInput.value.trim().toUpperCase()
                : "";

            if (code === "LUMINA10") {
                promoApplied = true;

                if (promoMessage) {
                    promoMessage.textContent =
                        "LUMINA10 applied successfully. You saved 10%!";

                    promoMessage.classList.add("success");
                }

            } else {
                promoApplied = false;

                if (promoMessage) {
                    promoMessage.textContent =
                        "Invalid code. Try LUMINA10.";

                    promoMessage.classList.remove("success");
                }
            }

            updateSummary();
        });
    }


// ================= CHECKOUT NAVIGATION =================

    if (checkoutButton) {
        checkoutButton.addEventListener("click", function () {

            if (cart.size === 0 || requestInProgress) {
                return;
            }

            window.location.href = "/checkout/";

        });
    }


    // ================= INITIAL LOAD =================

    if (checkoutButton) {
        checkoutButton.disabled = true;
    }

    loadCart();

})();
