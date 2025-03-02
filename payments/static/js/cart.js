document.addEventListener("DOMContentLoaded", function () {
    const checkoutButton = document.getElementById("checkout-button");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", function () {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

            const items = Array.from(document.querySelectorAll(".cart-item")).map(item => ({
                id: item.dataset.itemId,
                quantity: item.dataset.quantity
            }));

            const totalPrice = parseFloat(document.getElementById("total_price").textContent);

            fetch("/buy/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({items, total_price: totalPrice})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.session_id) {
                        const stripe = Stripe(data.stripe_public_key);
                        stripe.redirectToCheckout({sessionId: data.session_id})
                            .then(result => {
                                if (result.error) {
                                    console.error("Redirect error:", result.error);
                                }
                            });
                    } else {
                        console.error("Ошибка: Не получен session_id");
                    }
                })
                .catch(error => {
                    console.error("Ошибка:", error);
                });
        });
    }
});
