const express = require('express');
const cors = require('cors');

const app = express();

// Use CORS middleware
app.use(cors({
    origin: 'http://127.0.0.1:5500' // Replace this with the origin of your frontend
}));

app.use(express.json());

// Define your routes
app.post('/add_customer', (req, res) => {
    // Your logic to add a customer
    res.json({ message: 'Customer added successfully' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});


