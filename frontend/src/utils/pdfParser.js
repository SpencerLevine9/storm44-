import * as pdfjsLib from 'pdfjs-dist';

// Point PDF.js to its bundled worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.mjs',
  import.meta.url,
).toString();

/**
 * Parse a PDF from a URL and extract text per page.
 *
 * @param {string} url — URL to fetch the PDF from (e.g. /api/pdf-file/filename.pdf)
 * @returns {Promise<{ pages: Array<{ pageNum: number, text: string }>, totalText: string, totalChars: number }>}
 */
export async function parsePdf(url) {
  const pdf = await pdfjsLib.getDocument(url).promise;
  const pages = [];

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const text = content.items.map((item) => item.str).join(' ');
    pages.push({ pageNum: i, text });
  }

  const totalText = pages.map((p) => p.text).join('\n\n');

  return {
    pages,
    totalText,
    totalChars: totalText.length,
  };
}
