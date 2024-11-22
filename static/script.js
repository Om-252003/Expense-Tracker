// Handle transaction form submission
$("#transactionForm").on("submit", function (e) {
    e.preventDefault();

    const date = $("#date").val();
    const description = $("#description").val();
    const amount = parseFloat($("#amount").val());
    const category = $("#category").val();

    const submitButton = $(this).find('button');
    submitButton.prop('disabled', true);  // Disable the submit button to prevent double submission

    $.ajax({
        url: "/add_transaction",
        method: "POST",
        data: {
            date: date,
            description: description,
            amount: amount,
            category: category
        },
        success: function (response) {
            loadTransactions();
            $("#transactionForm")[0].reset();  // Clear the form

            // Show success message
            $("#successMessage").fadeIn(500).delay(2000).fadeOut(500); // Fades in, stays for 2s, then fades out

            // Re-enable the submit button
            submitButton.prop('disabled', false);
        },
        error: function() {
            submitButton.prop('disabled', false);  // Re-enable the submit button if error occurs
        }
    });
});

// Load all transactions
function loadTransactions() {
    $.ajax({
        url: "/filter_transactions",
        method: "GET",
        success: function (transactions) {
            renderTransactions(transactions);
        }
    });
}

// Render transactions in the table
function renderTransactions(transactions) {
    const tableBody = $("#transactionsTable tbody");
    tableBody.empty();
    transactions.forEach(transaction => {
        tableBody.append(`
            <tr>
                <td>${transaction.Date}</td>
                <td>${transaction.Description}</td>
                <td>${transaction.Amount}</td>
                <td>${transaction.Category}</td>
            </tr>
        `);
    });
}

// Function to fetch and display transaction summary
function fetchTransactionSummary() {
    let category = document.getElementById('filterCategory').value;
    let startDate = document.getElementById('startDate').value;
    let endDate = document.getElementById('endDate').value;
    let minAmount = document.getElementById('minAmount').value || 0;
    let maxAmount = document.getElementById('maxAmount').value || 1000000;

    // Send GET request to /transaction_summary with filters as parameters
    fetch(`/transaction_summary?category=${category}&start_date=${startDate}&end_date=${endDate}&min_amount=${minAmount}&max_amount=${maxAmount}`)
        .then(response => response.json())
        .then(data => {
            // Update the summary on the page
            document.getElementById('totalIncome').textContent = `$${data["Total Income"].toFixed(2)}`;
            document.getElementById('totalExpense').textContent = `$${data["Total Expense"].toFixed(2)}`;
            document.getElementById('balance').textContent = `$${data["Balance"].toFixed(2)}`;
        })
        .catch(error => console.error('Error fetching summary:', error));
}

// Call the function when the page loads or after a filter change
window.onload = fetchTransactionSummary;
document.getElementById('filterForm').onsubmit = function(e) {
    e.preventDefault();
    fetchTransactionSummary();
};

// script.js - Smooth transition for button clicks
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        // Smooth transition effect (e.g., fading out the page)
        document.body.style.transition = "opacity 0.5s ease";
        document.body.style.opacity = "0";

        setTimeout(() => {
            window.location.href = btn.href;
        }, 500); // Delay to allow transition effect
    });
});


// In static/script.js

document.getElementById("transactionForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent default form submission

    let formData = new FormData(this);  // Get the form data

    fetch("/add_transaction", {
        method: "POST",
        body: formData  // Send form data as a POST request
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);  // Show success message
        document.getElementById("transactionForm").reset();  // Clear form fields
    })
    .catch(error => {
        console.error("Error:", error);
    });
});




// Initially load transactions
loadTransactions();
