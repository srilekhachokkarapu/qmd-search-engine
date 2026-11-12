
// ==================================================
// QMD SEARCH ENGINE - FRONTEND JAVASCRIPT
// ==================================================


// Store previous search results
let lastSearchResults = [];


// ==================================================
// 1. GET HTML ELEMENTS
// ==================================================

const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const searchMode = document.getElementById("searchMode");
const collectionSelect = document.getElementById("collection");
const topKSelect = document.getElementById("topK");
const searchButton = document.getElementById("searchButton");

const resultsContainer = document.getElementById("resultsContainer");
const statusMessage = document.getElementById("statusMessage");


// ==================================================
// 2. LOAD COLLECTIONS FROM FASTAPI
// ==================================================

async function loadCollections() {

    try {

        const response = await fetch("/collections");

        if (!response.ok) {
            throw new Error("Unable to load collections.");
        }

        const data = await response.json();

        const collections = data.collections || [];

        collections.forEach((item) => {

            const collectionName =
                item.collection || item.name;

            if (!collectionName) return;

            const option = document.createElement("option");

            option.value = collectionName;
            option.textContent = collectionName;

            collectionSelect.appendChild(option);

        });

    } catch (error) {

        console.error("Collection loading error:", error);

        showStatus("Could not load collections.", "error");

    }
}


// ==================================================
// 3. DISPLAY STATUS MESSAGES
// ==================================================

function showStatus(message, type = "info") {

    statusMessage.textContent = message;

    statusMessage.className = `status-message ${type}`;

}


// ==================================================
// 4. DISPLAY SEARCH RESULTS
// ==================================================

function displayResults(results) {

    // Save results for Back to Results functionality
    lastSearchResults = results || [];

    resultsContainer.replaceChildren();


    // Handle empty results
    if (!results || results.length === 0) {

        const message = document.createElement("div");

        message.className = "empty-state";

        const heading = document.createElement("h2");

        heading.textContent = "No Results Found";

        const paragraph = document.createElement("p");

        paragraph.textContent =
            "Try another query or select a different search mode.";

        message.append(heading, paragraph);

        resultsContainer.appendChild(message);

        return;
    }


    // Create individual result cards
    results.forEach((result, index) => {

        const card = document.createElement("div");

        card.className = "result-card";


        // Result number
        const number = document.createElement("span");

        number.className = "result-number";

        number.textContent = `Result ${index + 1}`;


        // Document title
        const title = document.createElement("h3");

        title.textContent =
            result.document_title ||
            result.title ||
            result.file_name ||
            "Untitled Document";


        // Collection name
        const collection = document.createElement("p");

        collection.className = "result-meta";

        collection.textContent =
            `Collection: ${result.collection || "Unknown"}`;


        // Section heading
        const heading = document.createElement("p");

        heading.className = "result-heading";

        heading.textContent =
            `Section: ${result.heading || "Introduction"}`;


        // Matching content
        const content = document.createElement("p");

        content.className = "result-content";

        content.textContent = result.content || "";


        // Relevance score
        
// Relevance score
            const score = document.createElement("p");
            score.className = "result-score";

            if (
                result.hybrid_score !== undefined &&
                result.hybrid_score !== null
            ) {
                // Hybrid Search
                score.textContent =
                    `Hybrid Score: ${result.hybrid_score.toFixed(5)}`;

            } else if (
                result.similarity_score !== undefined &&
                result.similarity_score !== null
            ) {
                // Semantic Search
                score.textContent =
                    `Cosine Similarity: ${result.similarity_score.toFixed(5)}`;

            } else if (
                result.relevance_score !== undefined &&
                result.relevance_score !== null
            ) {
                // Keyword Search
                score.textContent =
                    `BM25 Relevance Score: ${result.relevance_score.toFixed(5)}`;

            } else {
                score.textContent = "Score: Not available";
            }
 


        // View complete document button
        const viewButton = document.createElement("button");

        viewButton.className = "view-document-btn";

        viewButton.textContent = "View Full Document";

        viewButton.addEventListener("click", () => {

            openDocument(result.document_id);

        });


        // Add all elements to card
        card.append(
            number,
            title,
            collection,
            heading,
            content,
            score,
            viewButton
        );


        resultsContainer.appendChild(card);

    });

}


// ==================================================
// 5. OPEN COMPLETE DOCUMENT USING DOCUMENT ID
// ==================================================

async function openDocument(documentId) {

    if (!documentId) {

        showStatus("Document ID is missing.", "error");

        return;

    }

    try {

        showStatus("Loading complete document...", "info");


        // Call existing FastAPI document endpoint
        const response = await fetch(
            `/documents/${encodeURIComponent(documentId)}`
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to load document."
            );

        }


        // Display complete document
        renderDocument(data);


        showStatus("Document loaded successfully.", "success");


    } catch (error) {

        console.error("Document loading error:", error);

        showStatus(error.message, "error");

    }

}


// ==================================================
// 6. RENDER COMPLETE DOCUMENT
// ==================================================

function renderDocument(data) {

    // Get document metadata
    const doc = data.document;

    // Get all document chunks
    const chunks = data.chunks || [];


    resultsContainer.replaceChildren();


    // Main document viewer
    const viewer = document.createElement("div");

    viewer.className = "document-viewer";


    // ----------------------------------------------
    // Back to Results button
    // ----------------------------------------------

    const backButton = document.createElement("button");

    backButton.className = "back-button";

    backButton.textContent = "← Back to Results";

    backButton.addEventListener("click", () => {

        displayResults(lastSearchResults);

        showStatus(
            `${lastSearchResults.length} search results`,
            "success"
        );

    });


    // ----------------------------------------------
    // Document title
    // ----------------------------------------------

    const title = document.createElement("h2");

    title.textContent = doc.title || "Untitled Document";


    // ----------------------------------------------
    // Document metadata
    // ----------------------------------------------

    const metadata = document.createElement("div");

    metadata.className = "document-metadata";


    const details = [

        `Document ID: ${doc.document_id || "Not available"}`,

        `Collection: ${doc.collection || "Unknown"}`,

        `Author: ${doc.author || "Unknown"}`,

        `Category: ${doc.category || "Unknown"}`,

        `Date: ${doc.date || "Not available"}`,

        `Total Words: ${doc.word_count ?? 0}`,

        `Total Chunks: ${data.total_chunks ?? chunks.length}`

    ];


    details.forEach((detail) => {

        const paragraph = document.createElement("p");

        paragraph.textContent = detail;

        metadata.appendChild(paragraph);

    });


    viewer.append(
        backButton,
        title,
        metadata
    );


    // ----------------------------------------------
    // Complete document content
    // ----------------------------------------------

    const contentSection = document.createElement("div");

    contentSection.className = "document-content";


    const contentHeading = document.createElement("h3");

    contentHeading.textContent = "Complete Document Content";

    contentSection.appendChild(contentHeading);


    // Display every chunk
    chunks.forEach((chunk, index) => {

        const section = document.createElement("div");

        section.className = "document-chunk";


        // Section heading
        const heading = document.createElement("h4");

        heading.textContent =
            chunk.heading || `Section ${index + 1}`;


        // Section hierarchy
        if (
            Array.isArray(chunk.heading_path) &&
            chunk.heading_path.length > 1
        ) {

            const path = document.createElement("p");

            path.className = "document-heading-path";

            path.textContent = chunk.heading_path.join(" > ");

            section.appendChild(path);

        }


        // Section content
        const content = document.createElement("p");

        content.textContent = chunk.content || "";


        section.append(
            heading,
            content
        );


        contentSection.appendChild(section);

    });


    viewer.appendChild(contentSection);


    resultsContainer.appendChild(viewer);

}


// ==================================================
// 7. PERFORM SEARCH
// ==================================================

async function performSearch(query) {

    const requestData = {

        query: query,

        mode: searchMode.value,

        top_k: Number(topKSelect.value),

        collection: collectionSelect.value || null

    };


    try {

        searchButton.disabled = true;

        searchButton.textContent = "Searching...";


        showStatus("Searching your documents...", "info");


        // Send request to FastAPI
        const response = await fetch("/search", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(requestData)

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Search request failed."
            );

        }


        // Display search results
        displayResults(data.results);


        showStatus(

            `${data.total_results} results found using ${data.mode} search.`,

            "success"

        );


    } catch (error) {

        console.error("Search error:", error);

        resultsContainer.replaceChildren();

        lastSearchResults = [];

        showStatus(error.message, "error");


    } finally {

        searchButton.disabled = false;

        searchButton.textContent = "Search";

    }

}


// ==================================================
// 8. HANDLE SEARCH FORM SUBMISSION
// ==================================================

searchForm.addEventListener("submit", function (event) {

    event.preventDefault();


    const query = searchInput.value.trim();


    if (!query) {

        showStatus("Please enter a search query.", "error");

        searchInput.focus();

        return;

    }


    performSearch(query);

});


// ==================================================
// 9. INITIALIZE APPLICATION
// ==================================================

// Load collections when homepage opens
loadCollections();
