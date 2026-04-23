"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
let client;
function activate(context) {
    // Server implementation path
    const serverModule = context.asAbsolutePath(path.join('server', 'server.py'));
    // Server options for Python Language Server
    const serverOptions = {
        run: { command: 'python', args: [serverModule] },
        debug: { command: 'python', args: [serverModule] }
    };
    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'sindlish' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.sd')
        }
    };
    // Setup Diagnostic System
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('sindlish');
    context.subscriptions.push(diagnosticCollection);
    // Create and start the client
    client = new node_1.LanguageClient('sindlishLanguageServer', 'Sindlish Language Server', serverOptions, {
        ...clientOptions,
        traceOutputChannel: vscode.window.createOutputChannel('Sindlish Language Server Trace')
    });
    // Explicitly listen to publishDiagnostics to update the collection
    client.onNotification('textDocument/publishDiagnostics', (params) => {
        console.log('PublishDiagnostics Notification Received:', params);
        const uri = vscode.Uri.parse(params.uri);
        const diagnostics = params.diagnostics.map((d) => new vscode.Diagnostic(new vscode.Range(d.range.start.line, d.range.start.character, d.range.end.line, d.range.end.character), d.message, vscode.DiagnosticSeverity.Error));
        diagnosticCollection.set(uri, diagnostics);
    });
    client.start();
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map