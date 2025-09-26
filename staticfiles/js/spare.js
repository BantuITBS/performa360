function handleUserSelection() {
    const userSelect = document.getElementById('user-select');
    const customUserCountInput = document.getElementById('custom-user-count');
  
    if (userSelect.value === 'custom') {
      customUserCountInput.disabled = false;
    } else {
      customUserCountInput.disabled = true;
      customUserCountInput.value = '';
      userSelect.value = userSelect.value; // Set the selected value back to the original value
    }
  }
      function calculateReviews() {
          const startDate = new Date(document.getElementById('start_date').value);
          const endDate = new Date(document.getElementById('end_date').value);
          const reviewCycle = document.getElementById('review_cycle').value;
          
          // Check if the dates are valid
          if (isNaN(startDate) || isNaN(endDate) || startDate >= endDate) {
              document.getElementById('review_number').value = '';  // Clear if invalid date
              alert("Please enter valid dates.");
              return;
          }
  
          // Calculate the number of days between the dates
          const timeDiff = endDate - startDate;
          const daysDiff = timeDiff / (1000 * 3600 * 24);  // Convert time difference to days
  
          // Calculate the maximum number of reviews based on the cycle
          let maxReviews = 0;
  
          switch (reviewCycle) {
              case 'Weekly':
                  maxReviews = Math.floor(daysDiff / 7);
                  break;
              case 'Monthly':
                  maxReviews = Math.floor(daysDiff / 30);  // Approximate 30 days per month
                  break;
              case 'Quarterly':
                  maxReviews = Math.floor(daysDiff / 90);  // Approximate 90 days per quarter
                  break;
              case 'Bi-Annually':
                  maxReviews = Math.floor(daysDiff / 180);  // Approximate 180 days per half year
                  break;
              case 'Annually':
                  maxReviews = Math.floor(daysDiff / 365);  // Approximate 365 days per year
                  break;
              default:
                  document.getElementById('review_number').value = '';  // Clear if no cycle selected
                  return;
          }

// Populate the review_number field with the calculated value
            document.getElementById('review_number').value = maxReviews;
        }
    
        // Event listeners to recalculate when user changes dates or review cycle
        document.getElementById('start_date').addEventListener('change', calculateReviews);
        document.getElementById('end_date').addEventListener('change', calculateReviews);
        document.getElementById('review_cycle').addEventListener('change', calculateReviews);
    
                document.addEventListener('DOMContentLoaded', () => {
                    const regionSelect = document.getElementById('region');
                
                    // Initialize Select2 with free-text entry capability
                    $(regionSelect).select2({
                        tags: true, // Allow free-text entry
                        placeholder: "Select or enter a Region/Branch",
                        allowClear: true, // Allow clearing the selection
                    });            
                });
                
                document.addEventListener('DOMContentLoaded', () => {
        const regionSelect = document.getElementById('region');
    
        // Initialize Select2 with free-text entry capability
        $(regionSelect).select2({
            tags: true, // Allow free-text entry
            placeholder: "Select or enter a Region/Branch",
            allowClear: true, // Allow clearing the selection
        });
    
        // Dynamically populate the options (example placeholder logic)
        const regions = ['East', 'West', 'North', 'South'];
        regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            regionSelect.appendChild(option);
        });
    });
    
    // Trigger cost calculation when any of the input values change
    document.getElementById('country').addEventListener('change', calculateCost);
    document.getElementById('user-select').addEventListener('change', handleUserSelection);
    document.getElementById('payment-plan').addEventListener('change', calculateCost);
    
    // Handle Custom User Input
    function handleUserSelection() {
        const userSelect = document.getElementById('user-select').value;
        const customInput = document.getElementById('custom-users');
    
        if (userSelect === 'custom') {
            customInput.style.display = 'block'; // Show custom input field
        } else {
            customInput.style.display = 'none'; // Hide custom input field
        }
    
        calculateCost(); // Trigger cost recalculation
    }
    
    // Optional validation for custom input (ensuring it's a positive number)
    function validateCustomInput() {
        const customInputValue = document.getElementById('custom-users-input').value;
        if (customInputValue <= 0) {
            alert("Please enter a valid number of users.");
        }
    }
    
    // Function to handle country and payment plan changes
    async function calculateCost() {
        const country = document.getElementById('country').value;
        const userCountInput = document.getElementById('user-select').value === 'custom'
            ? parseInt(document.getElementById('custom-users-input').value)
            : parseInt(document.getElementById('user-select').value.split('-')[1]); // Max of the range (e.g., "1-50" -> 50)
    
        const paymentPlan = document.getElementById('payment-plan').value;
    
        if (isNaN(userCountInput) || userCountInput <= 0) {
            alert('Please enter a valid number of users.');
            return;
        }
    
        // Base rate in ZAR (assumed example, can be changed based on your pricing model)
        const baseRateZAR = 50;
    
        // Fetch the exchange rate based on the selected country (ZAR to selected country)
        let exchangeRate = 0;
        let exchangeRateMessage = '';
        
        if (country !== 'ZAR') {
            try {
                const response = await fetch(`https://api.exchangerate-api.com/v4/latest/ZAR`);
                const rateData = await response.json();
                exchangeRate = rateData.rates[country];
    
                if (!exchangeRate) {
                    throw new Error(`Exchange rate for ${country} not available.`);
                }
    
                exchangeRateMessage = `1 ZAR = ${exchangeRate.toFixed(2)} ${country}`;
            } catch (error) {
                console.error('Error fetching exchange rate:', error);
                alert('Could not fetch the exchange rate. Please try again later.');
                return;
            }
        } else {
            exchangeRate = 1; // If selected country is ZAR, no conversion needed
            exchangeRateMessage = 'Cost in ZAR';
        }
    
        // Display exchange rate message (if applicable)
        document.getElementById('exchangeRateDisplay').textContent = exchangeRateMessage;
    
        // Pricing logic with discounts
        const discountRates = [0.0, 0.05, 0.10, 0.15, 0.20]; // Discounts for each subsequent bucket of 50 users
    
        let totalCostZAR = 0;
        let remainingUsers = userCountInput;
    
        // Calculate bucket-based costs
        for (let i = 0; remainingUsers > 0; i++) {
            const usersInBucket = Math.min(remainingUsers, 50); // Max 50 users per bucket
            const discount = i < discountRates.length ? discountRates[i] : discountRates[discountRates.length - 1]; // Use last discount for extra buckets
            const costPerUser = baseRateZAR * (1 - discount); // Use ZAR for calculation
            totalCostZAR += usersInBucket * costPerUser;
            remainingUsers -= usersInBucket;
        }
    
        // Apply payment plan multiplier
        let periodMultiplier;
        let periodDiscount = 0;
        if (paymentPlan === 'quarterly') {
            periodMultiplier = 3; // 3 months
            periodDiscount = 0.02; // 2% discount
        } else if (paymentPlan === 'semi-annually') {
            periodMultiplier = 6; // 6 months
            periodDiscount = 0.05; // 5% discount
        } else if (paymentPlan === 'annually') {
            periodMultiplier = 12; // 12 months
            periodDiscount = 0.07; // 7% discount
        } else {
            periodMultiplier = 1; // Monthly
        }
    
        totalCostZAR = totalCostZAR * periodMultiplier * (1 - periodDiscount);
    
        // Convert total cost to the selected currency
        let totalCostConverted;
        if (country !== 'ZAR') {
            totalCostConverted = totalCostZAR * exchangeRate; // Convert ZAR to selected currency
            document.getElementById('total-cost').value = `${totalCostConverted.toFixed(2)} ${country}`;
        } else {
            // Display cost in ZAR
            totalCostConverted = totalCostZAR;
            document.getElementById('total-cost').value = `${totalCostConverted.toFixed(2)} ZAR`;
        }
    };
    
                    document.addEventListener('DOMContentLoaded', () => {
                        const passwordInput = document.getElementById('password');
                        const confirmPasswordInput = document.getElementById('confirm_password');
                        const passwordHelp = document.getElementById('passwordHelp');
                        const passwordMatchMessage = document.getElementById('passwordMatchMessage');
                        const togglePassword = document.getElementById('togglePassword');
                        const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
                
                        const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
                
                        // Toggle password visibility
                        togglePassword.addEventListener('click', () => {
                            passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
                            togglePassword.textContent = togglePassword.textContent === 'Show' ? 'Hide' : 'Show';
                        });
                
                        toggleConfirmPassword.addEventListener('click', () => {
                            confirmPasswordInput.type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
                            toggleConfirmPassword.textContent = toggleConfirmPassword.textContent === 'Show' ? 'Hide' : 'Show';
                        });
                
                        // Validate password strength
                        passwordInput.addEventListener('input', () => {
                            if (!passwordRegex.test(passwordInput.value)) {
                                passwordHelp.style.color = 'red';
                            } else {
                                passwordHelp.style.color = 'green';
                            }
                        });
                
                        // Check if passwords match
                        confirmPasswordInput.addEventListener('input', () => {
                            if (confirmPasswordInput.value !== passwordInput.value) {
                                passwordMatchMessage.textContent = 'Passwords do not match.';
                            } else {
                                passwordMatchMessage.textContent = '';
                            }
                        });
                    });
    
            document.addEventListener('DOMContentLoaded', () => {
                const form = document.getElementById('signup-form');
                const submitButton = form.querySelector('button[type="submit"]');
        
                // Handle click event on the submit button
                submitButton.addEventListener('click', (event) => {
                    event.preventDefault(); // Prevent default form submission
        
                    // Validate the form before proceeding
                    if (validateForm()) {
                        // Redirect to PayPal
                        window.location.href = 'https://www.paypal.com/checkout';
                    }
                });
            });
        
            function validateForm() {
                // Fields to validate
                const fieldsToValidate = [
                    'company',
                    'country',
                    'region',
                    'start_date',
                    'end_date',
                    'review_cycle',
                    'email',
                    'password',
                    'confirm_password'
                ];
        
                let allFilled = true;
        
                // Check each required field
                fieldsToValidate.forEach(fieldId => {
                    const field = document.getElementById(fieldId);
        
                    if (!field || !field.value.trim()) {
                        allFilled = false;
                        field.style.borderColor = 'red'; // Highlight missing fields
                    } else {
                        field.style.borderColor = '#ccc'; // Reset border color for valid fields
                    }
                });
        
                // Validate password match
                const password = document.getElementById('password');
                const confirmPassword = document.getElementById('confirm_password');
                const passwordMatchMessage = document.getElementById('passwordMatchMessage');
        
                if (password.value !== confirmPassword.value) {
                    allFilled = false;
                    password.style.borderColor = 'red';
                    confirmPassword.style.borderColor = 'red';
                    passwordMatchMessage.textContent = 'Passwords do not match.';
                } else {
                    password.style.borderColor = '#ccc';
                    confirmPassword.style.borderColor = '#ccc';
                    passwordMatchMessage.textContent = '';
                }
        
                // If any field is invalid, alert and prevent redirection
                if (!allFilled) {
                    alert('Please fill all required fields correctly before proceeding.');
                }
        
                return allFilled; // Return true only if all fields are correctly filled
            }
    
        // Load PayPal script dynamically
        function loadPayPal() {
            const script = document.createElement('script');
            script.src = "https://www.paypal.com/sdk/js";  // PayPal script with no client-id or amount
            script.onload = () => {
                console.log("PayPal script loaded successfully.");
            };
            document.body.appendChild(script);
        }
    
        window.onload = function() {
            loadPayPal();  // Load PayPal script
            populateUserSelect();  // Populate user select dropdown
        };
    
    // Populate country dropdown
    document.addEventListener('DOMContentLoaded', () => {
        const countrySelect = document.getElementById('country');
        const exchangeRateDisplay = document.getElementById('exchangeRateDisplay');
    
        // Fetch countries and currencies from the REST Countries API
        fetch('https://restcountries.com/v3.1/all')
            .then(response => response.json())
            .then(data => {
                // Filter countries with currency data
                const countriesWithCurrencies = data.filter(country => country.currencies);
    
                // Sort countries alphabetically by name
                countriesWithCurrencies.sort((a, b) => a.name.common.localeCompare(b.name.common));
    
                // Populate the dropdown with sorted countries
                countriesWithCurrencies.forEach(country => {
                    const currencyCodes = Object.keys(country.currencies).join(", ");
                    const option = document.createElement('option');
                    option.value = `${country.name.common},${currencyCodes}`; // Add country and currency
                    option.textContent = `${country.name.common} (${currencyCodes})`;
                    countrySelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching country data:', error);
            });
    
        // Event listener for dropdown change to fetch the exchange rate
        countrySelect.addEventListener('change', () => {
            const selectedValue = countrySelect.value;
            if (selectedValue) {
                const [countryName, currencyCode] = selectedValue.split(','); // Extract country name and currency code
                const trimmedCurrencyCode = currencyCode.trim(); // Remove any extra spaces
    
                if (trimmedCurrencyCode) {
                    if (trimmedCurrencyCode === 'USD' && countryName === 'Zimbabwe') {
                        // Special case for Zimbabwe (uses USD as currency)
                        exchangeRateDisplay.textContent = `1 USD = 1 USD`;
                    } else if (trimmedCurrencyCode === 'ZAR' && countryName === 'South Africa') {
                        // Special case for South Africa (uses ZAR currency)
                        fetch(`https://api.exchangerate-api.com/v4/latest/USD`) // Base currency: USD
                            .then(response => response.json())
                            .then(rateData => {
                                const exchangeRate = rateData.rates['ZAR']; // Get the exchange rate for ZAR
                                if (exchangeRate) {
                                    exchangeRateDisplay.textContent = `1 USD = ${exchangeRate} ZAR`;
                                } else {
                                    exchangeRateDisplay.textContent = `Exchange Rate unavailable for ZAR`;
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching exchange rate:', error);
                                exchangeRateDisplay.textContent = 'Error fetching exchange rate.';
                            });
                    } else {
                        // For all other currencies, fetch exchange rate from USD to selected currency
                        fetch(`https://api.exchangerate-api.com/v4/latest/USD`) // Base currency: USD
                            .then(response => response.json())
                            .then(rateData => {
                                const exchangeRate = rateData.rates[trimmedCurrencyCode];
                                if (exchangeRate) {
                                    exchangeRateDisplay.textContent = `1 USD = ${exchangeRate} ${trimmedCurrencyCode}`;
                                } else {
                                    exchangeRateDisplay.textContent = `Exchange Rate unavailable for ${trimmedCurrencyCode}`;
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching exchange rate:', error);
                                exchangeRateDisplay.textContent = 'Error fetching exchange rate.';
                            });
                    }
                }
            }
        });
    });
    
    // Populate country dropdown
    document.addEventListener('DOMContentLoaded', () => {
        const countrySelect = document.getElementById('country');
        const exchangeRateDisplay = document.getElementById('exchangeRateDisplay');
    
        // Fetch countries and currencies from the REST Countries API
        fetch('https://restcountries.com/v3.1/all')
            .then(response => response.json())
            .then(data => {
                // Filter countries with currency data
                const countriesWithCurrencies = data.filter(country => country.currencies);
    
                // Sort countries alphabetically by name
                countriesWithCurrencies.sort((a, b) => a.name.common.localeCompare(b.name.common));
    
                // Populate the dropdown with sorted countries
                countriesWithCurrencies.forEach(country => {
                    const currencyCodes = Object.keys(country.currencies).join(", ");
                    const option = document.createElement('option');
                    option.value = `${country.name.common},${currencyCodes}`; // Add country and currency
                    option.textContent = `${country.name.common} (${currencyCodes})`;
                    countrySelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching country data:', error);
            });
    
        // Event listener for dropdown change to fetch the exchange rate
        countrySelect.addEventListener('change', () => {
            const selectedValue = countrySelect.value;
            if (selectedValue) {
                const [countryName, currencyCode] = selectedValue.split(','); // Extract country name and currency code
                const trimmedCurrencyCode = currencyCode.trim(); // Remove any extra spaces
    
                if (trimmedCurrencyCode) {
                    if (trimmedCurrencyCode === 'USD' && countryName === 'Zimbabwe') {
                        // Special case for Zimbabwe (uses USD as currency)
                        exchangeRateDisplay.textContent = `1 USD = 1 USD`;
                    } else if (trimmedCurrencyCode === 'ZAR' && countryName === 'South Africa') {
                        // Special case for South Africa (uses ZAR currency)
                        fetch(`https://api.exchangerate-api.com/v4/latest/USD`) // Base currency: USD
                            .then(response => response.json())
                            .then(rateData => {
                                const exchangeRate = rateData.rates['ZAR']; // Get the exchange rate for ZAR
                                if (exchangeRate) {
                                    exchangeRateDisplay.textContent = `1 USD = ${exchangeRate} ZAR`;
                                } else {
                                    exchangeRateDisplay.textContent = `Exchange Rate unavailable for ZAR`;
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching exchange rate:', error);
                                exchangeRateDisplay.textContent = 'Error fetching exchange rate.';
                            });
                    } else {
                        // For all other currencies, fetch exchange rate from USD to selected currency
                        fetch(`https://api.exchangerate-api.com/v4/latest/USD`) // Base currency: USD
                            .then(response => response.json())
                            .then(rateData => {
                                const exchangeRate = rateData.rates[trimmedCurrencyCode];
                                if (exchangeRate) {
                                    exchangeRateDisplay.textContent = `1 USD = ${exchangeRate} ${trimmedCurrencyCode}`;
                                } else {
                                    exchangeRateDisplay.textContent = `Exchange Rate unavailable for ${trimmedCurrencyCode}`;
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching exchange rate:', error);
                                exchangeRateDisplay.textContent = 'Error fetching exchange rate.';
                            });
                    }
                }
            }
        });
    });
    
        // Populate User Select Dropdown with Intervals
        function populateUserSelect() {
            const userSelect = document.getElementById('user-select');
            // Example: Populate with user intervals
            for (let i = 1; i <= 10000; i += 50) {
                const option = document.createElement('option');
                option.value = `${i}-${i + 50 - 1}`;
                option.text = `${i} - ${i + 50 - 1}`;
                userSelect.appendChild(option);
            }
        }
    
        // Handle Custom User Input
        function handleUserSelection() {
            const userSelect = document.getElementById('user-select').value;
            const customInput = document.getElementById('custom-users');
            
            // Show or hide custom input field based on selection
            if (userSelect === 'custom') {
                customInput.style.display = 'block';  // Show custom input field
            } else {
                customInput.style.display = 'none';  // Hide custom input field
            }
        }
    
        // Validate Custom Number of Users input (positive integer only)
        function validateCustomInput() {
            const customInput = document.getElementById('custom-users-input');
            const value = customInput.value;
    
            // If the input is not a positive integer, show an alert
            if (value && !/^[1-9][0-9]*$/.test(value)) {
                customInput.setCustomValidity("Please enter a positive integer.");
            } else {
                customInput.setCustomValidity("");  // Reset the custom validity if input is valid
            }
        }
    
        // Form validation
        function validateForm() {
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm_password").value;
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
            if (!emailPattern.test(email)) {
                alert("Please enter a valid email address.");
                return false;
            }
    
            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return false;
            }
    
            return true;
        }
    