
const CHUNK_SIZE = 10;
let rawData = "Book 1\nBook 2\nBook 3\nBook 4\nBook 5\n";
let processedData = rawData;
let books = [];
let isProcessing = false;

function parseDataChunk(chunk, append = false) {
  const lines = chunk.split('\n');
  const parsed = [];
  for (let line of lines) {
    if (line.trim()) parsed.push(line.trim());
  }

  if (append) {
    books = books.concat(parsed);
  } else {
    books = parsed;
  }
}

function processDataChunk() {
  if (isProcessing) return;
  isProcessing = true;

  const chunkEnd = Math.min(CHUNK_SIZE, processedData.length);
  const chunkToProcess = processedData.substring(0, chunkEnd);
  const remainingData = processedData.substring(chunkEnd);

  console.log(`Processing chunk: "${chunkToProcess.replace(/\n/g, '\\n')}"`);

  // ORIGINAL CALL: no append arg
  parseDataChunk(chunkToProcess);

  console.log("Books after chunk:", books);

  if (remainingData.length > 0) {
    processedData = remainingData;
    isProcessing = false;
    processDataChunk();
  } else {
    console.log("Finished. Total books:", books.length);
  }
}

processDataChunk();
