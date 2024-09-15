const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors()); // Allow all origins
app.use(express.json()); // For parsing application/json

// Your route handlers
app.post('/add_customer', (_req, _res) => {
    // Your logic here
});

// Add other routes similarly...

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

app.use(cors({
    origin: 'https://library-management-system-api-4w5t.onrender.com' // Replace with the actual origin of your frontend
}));
