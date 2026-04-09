/* global process, Buffer */
/**
 * Vite Dev Server Plugin — local file storage for development only.
 *
 * Adds endpoints:
 *   POST   /api/upload-pdf    — save a PDF to tempPDFfolder/
 *   GET    /api/list-pdfs     — list files in tempPDFfolder/
 *   DELETE /api/delete-pdf/:filename — remove a file from tempPDFfolder/
 *   GET    /api/youtube-title — proxy YouTube oEmbed to avoid CORS
 */

import fs from 'node:fs';
import path from 'node:path';

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB

function sanitizeFilename(name) {
  return name
    .replace(/\.\./g, '')          // strip path traversal
    .replace(/[/\\:*?"<>|]/g, '_') // replace illegal chars
    .trim();
}

export default function devFilesPlugin() {
  const uploadDir = path.resolve(process.cwd(), 'tempPDFfolder');

  return {
    name: 'vite-plugin-dev-files',
    configureServer(server) {
      // Ensure upload directory exists
      if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true });
      }

      server.middlewares.use(async (req, res, next) => {
        // ─── POST /api/upload-pdf ───────────────────────────
        if (req.method === 'POST' && req.url === '/api/upload-pdf') {
          try {
            const chunks = [];
            let totalSize = 0;

            for await (const chunk of req) {
              totalSize += chunk.length;
              if (totalSize > MAX_FILE_SIZE) {
                res.writeHead(413, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'File exceeds 25 MB limit' }));
                return;
              }
              chunks.push(chunk);
            }

            const body = Buffer.concat(chunks);

            // Parse multipart boundary from content-type
            const contentType = req.headers['content-type'] || '';
            const boundaryMatch = contentType.match(/boundary=(?:"([^"]+)"|([^\s;]+))/);
            if (!boundaryMatch) {
              res.writeHead(400, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Missing multipart boundary' }));
              return;
            }
            const boundary = boundaryMatch[1] || boundaryMatch[2];

            // Simple multipart parser — extract first file part
            const boundaryBuf = Buffer.from(`--${boundary}`);
            const parts = [];
            let start = body.indexOf(boundaryBuf) + boundaryBuf.length;

            while (start < body.length) {
              const end = body.indexOf(boundaryBuf, start);
              if (end === -1) break;
              parts.push(body.subarray(start, end));
              start = end + boundaryBuf.length;
            }

            if (parts.length === 0) {
              res.writeHead(400, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'No file found in upload' }));
              return;
            }

            const part = parts[0];
            const headerEnd = part.indexOf('\r\n\r\n');
            if (headerEnd === -1) {
              res.writeHead(400, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Malformed multipart data' }));
              return;
            }

            const headers = part.subarray(0, headerEnd).toString();
            const filenameMatch = headers.match(/filename="([^"]+)"/);
            const rawFilename = filenameMatch ? filenameMatch[1] : `upload-${Date.now()}.pdf`;
            const filename = sanitizeFilename(rawFilename);

            // Strip trailing \r\n before next boundary
            let fileData = part.subarray(headerEnd + 4);
            if (fileData[fileData.length - 2] === 0x0d && fileData[fileData.length - 1] === 0x0a) {
              fileData = fileData.subarray(0, fileData.length - 2);
            }

            const filePath = path.join(uploadDir, filename);
            fs.writeFileSync(filePath, fileData);

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ filename, size: fileData.length }));
          } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
          }
          return;
        }

        // ─── GET /api/list-pdfs ─────────────────────────────
        if (req.method === 'GET' && req.url === '/api/list-pdfs') {
          try {
            const files = fs.readdirSync(uploadDir).map((name) => ({
              name,
              size: fs.statSync(path.join(uploadDir, name)).size,
            }));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ files }));
          } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
          }
          return;
        }

        // ─── DELETE /api/delete-pdf/:filename ───────────────
        if (req.method === 'DELETE' && req.url?.startsWith('/api/delete-pdf/')) {
          try {
            const filename = sanitizeFilename(decodeURIComponent(req.url.slice('/api/delete-pdf/'.length)));
            const filePath = path.join(uploadDir, filename);

            if (fs.existsSync(filePath)) {
              fs.unlinkSync(filePath);
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ deleted: filename }));
            } else {
              res.writeHead(404, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'File not found' }));
            }
          } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
          }
          return;
        }

        // ─── GET /api/youtube-title?url=... ─────────────────
        if (req.method === 'GET' && req.url?.startsWith('/api/youtube-title')) {
          try {
            const reqUrl = new URL(req.url, 'http://localhost');
            const videoUrl = reqUrl.searchParams.get('url');

            if (!videoUrl) {
              res.writeHead(400, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Missing url parameter' }));
              return;
            }

            const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(videoUrl)}&format=json`;
            const response = await fetch(oembedUrl);

            if (!response.ok) {
              res.writeHead(response.status, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'YouTube oEmbed request failed' }));
              return;
            }

            const data = await response.json();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ title: data.title }));
          } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
          }
          return;
        }

        // ─── Serve files from tempPDFfolder ─────────────────
        if (req.method === 'GET' && req.url?.startsWith('/api/pdf-file/')) {
          try {
            const filename = sanitizeFilename(decodeURIComponent(req.url.slice('/api/pdf-file/'.length)));
            const filePath = path.join(uploadDir, filename);

            if (!fs.existsSync(filePath)) {
              res.writeHead(404, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'File not found' }));
              return;
            }

            const fileBuffer = fs.readFileSync(filePath);
            res.writeHead(200, {
              'Content-Type': 'application/pdf',
              'Content-Length': fileBuffer.length,
            });
            res.end(fileBuffer);
          } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
          }
          return;
        }

        next();
      });
    },
  };
}
