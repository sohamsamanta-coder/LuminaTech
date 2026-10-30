
(function () {
    "use strict";

    const CART_STORAGE_KEY = "luminaTechCart";

    const cartItems = document.getElementById("cartItems");
    const emptyState = document.getElementById("cartEmptyState");
    const checkoutButton = document.getElementById("checkoutButton");

    if (!cartItems) {
        return;
    }

    const productSources = document.querySelectorAll(".cart-product-source");

    const catalogue = new Map();

    productSources.forEach(function (source) {
        const image = source.querySelector("img");

        catalogue.set(String(source.dataset.id), {
            id: String(source.dataset.id),
            name: source.dataset.name,
            category: source.dataset.category,
            price: Number(source.dataset.price),
            image: image ? image.src : ""
        });
    });


    // Read previously saved cart items
    function loadCart() {
        try {
            const savedCart = JSON.parse(
                localStorage.getItem(CART_STORAGE_KEY) || "[]"
            );

            if (Array.isArray(savedCart)) {
                return new Map(
                    savedCart.map(id => [String(id), 1])
                );
            }

            if (savedCart && typeof savedCart === "object") {
                return new Map(
                    Object.entries(savedCart)
                        .map(([id, quantity]) => [
                            String(id),
                            Math.max(1, parseInt(quantity, 10) || 1)
                        ])
                );
            }

            return new Map();

        } catch (error) {
            console.warn("Could not load cart.", error);
            return new Map();
        }
    }


    let cart = loadCart();
    let promoApplied = false;


    // Save cart quantities
    function saveCart() {
        localStorage.setItem(
            CART_STORAGE_KEY,
            JSON.stringify(Object.fromEntries(cart))
        );
    }


    // Format prices in Indian Rupees
    function formatPrice(amount) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(amount);
    }


    // Count all cart quantities
    function getTotalQuantity() {
        return [...cart.values()].reduce(
            (total, quantity) => total + quantity,
            0
        );
    }


    // Create one cart product row
    function createCartItem(product, quantity) {
        const item = document.createElement("article");
        item.className = "cart-item";
        item.dataset.productId = product.id;

        // Product image
        const imageBox = document.createElement("div");
        imageBox.className = "cart-item-image";

        const image = document.createElement("img");
        image.src = product.image;
        image.alt = product.name;

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
            formatPrice(product.price * quantity) + " total";

        information.append(category, name, price, lineTotal);

        // Quantity and remove controls
        const actions = document.createElement("div");
        actions.className = "cart-item-actions";

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "cart-remove-button";
        removeButton.dataset.cartAction = "remove";
        removeButton.setAttribute("aria-label", "Remove " + product.name);
        removeButton.innerHTML =
            '<i class="fa-solid fa-trash-can"></i>';

        const quantityControl = document.createElement("div");
        quantityControl.className = "quantity-control";

        const decreaseButton = document.createElement("button");
        decreaseButton.type = "button";
        decreaseButton.dataset.cartAction = "decrease";
        decreaseButton.setAttribute("aria-label", "Decrease quantity");
        decreaseButton.innerHTML =
            '<i class="fa-solid fa-minus"></i>';

        const quantityNumber = document.createElement("span");
        quantityNumber.className = "quantity-number";
        quantityNumber.textContent = quantity;

        const increaseButton = document.createElement("button");
        increaseButton.type = "button";
        increaseButton.dataset.cartAction = "increase";
        increaseButton.setAttribute("aria-label", "Increase quantity");
        increaseButton.innerHTML =
            '<i class="fa-solid fa-plus"></i>';

        quantityControl.append(
            decreaseButton,
            quantityNumber,
            increaseButton
        );

        actions.append(removeButton, quantityControl);

        item.append(imageBox, information, actions);

        return item;
    }


    // Update the order summary
    function updateSummary(subtotal) {
        const deliveryFee =
            subtotal === 0 || subtotal >= 10000 ? 0 : 99;

        const discount = promoApplied
            ? Math.round(subtotal * 0.10)
            : 0;

        const total = subtotal + deliveryFee - discount;

        document.getElementById("cartSubtotal").textContent =
            formatPrice(subtotal);

        document.getElementById("cartDelivery").textContent =
            deliveryFee === 0 ? "FREE" : formatPrice(deliveryFee);

        document.getElementById("cartDiscount").textContent =
            "-" + formatPrice(discount);

        document.getElementById("cartTotal").textContent =
            formatPrice(total);

        document.getElementById("cartDiscountRow").hidden =
            !promoApplied || subtotal === 0;
    }


    // Render all cart products
    function renderCart() {
        cartItems.replaceChildren();

        let subtotal = 0;

        // Remove products that no longer exist in the database
        for (const productId of cart.keys()) {
            if (!catalogue.has(productId)) {
                cart.delete(productId);
            }
        }

        cart.forEach(function (quantity, productId) {
            const product = catalogue.get(productId);

            if (!product) {
                return;
            }

            subtotal += product.price * quantity;

            cartItems.appendChild(
                createCartItem(product, quantity)
            );
        });

        saveCart();

        const itemCount = getTotalQuantity();
        const itemLabel = itemCount === 1 ? "item" : "items";

        document.getElementById("cart-heading-count").textContent =
            itemCount + " " + itemLabel;

        document.getElementById("cart-items-count").textContent =
            itemCount + " " + itemLabel;

        const headerCount = document.getElementById("cartCount");

        if (headerCount) {
            headerCount.textContent = itemCount;
            headerCount.hidden = itemCount === 0;
        }

        emptyState.hidden = itemCount !== 0;

        updateSummary(subtotal);

        if (checkoutButton) {
            checkoutButton.disabled = itemCount === 0;
        }
    }


    // Handle quantity and remove buttons
    cartItems.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-cart-action]");

        if (!button) {
            return;
        }

        const item = button.closest(".cart-item");

        if (!item) {
            return;
        }

        const productId = item.dataset.productId;
        const action = button.dataset.cartAction;
        const currentQuantity = cart.get(productId) || 0;

        if (action === "increase") {
            cart.set(productId, currentQuantity + 1);
        }

        if (action === "decrease" && currentQuantity > 1) {
            cart.set(productId, currentQuantity - 1);
        }

        if (action === "remove") {
            cart.delete(productId);
        }

        renderCart();
    });


    // Apply a demonstration coupon
    const applyPromo = document.getElementById("applyPromo");
    const promoInput = document.getElementById("promoCode");
    const promoMessage = document.getElementById("promoMessage");

    if (applyPromo) {
        applyPromo.addEventListener("click", function () {
            const code = promoInput.value.trim().toUpperCase();

            if (code === "LUMINA10") {
                promoApplied = true;
                promoMessage.textContent =
                    "LUMINA10 applied successfully. You saved 10%!";
                promoMessage.classList.add("success");
            } else {
                promoApplied = false;
                promoMessage.textContent =
                    "Invalid code. Try LUMINA10.";
                promoMessage.classList.remove("success");
            }

            renderCart();
        });
    }


    // Checkout placeholder
    if (checkoutButton) {
        checkoutButton.addEventListener("click", function () {
            if (cart.size === 0) {
                return;
            }

            alert(
                "Your cart is ready! Payment and checkout integration will be added next."
            );
        });
    }


    renderCart();

})();
