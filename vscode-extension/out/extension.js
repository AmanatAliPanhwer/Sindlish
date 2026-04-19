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
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
let diagnosticCollection;
function activate(context) {
    // 1. Setup Auto-completion and Suggestions natively via built definitions
    const defsPath = path.join(context.extensionPath, 'syntaxes', 'sindlish-definitions.json');
    if (fs.existsSync(defsPath)) {
        const defs = JSON.parse(fs.readFileSync(defsPath, 'utf8'));
        const provider = vscode.languages.registerCompletionItemProvider('sindlish', {
            provideCompletionItems(document, position) {
                const completions = [];
                defs.keywords.forEach((kw) => {
                    const item = new vscode.CompletionItem(kw, vscode.CompletionItemKind.Keyword);
                    completions.push(item);
                });
                defs.functions.forEach((fn) => {
                    const item = new vscode.CompletionItem(fn, vscode.CompletionItemKind.Function);
                    completions.push(item);
                });
                defs.methods.forEach((m) => {
                    const item = new vscode.CompletionItem(m, vscode.CompletionItemKind.Method);
                    completions.push(item);
                });
                return completions;
            }
        }, '.'); // Trigger on dot for method completions too
        context.subscriptions.push(provider);
    }
    // 2. Setup Diagnostic System (Native Linting via CLI)
    diagnosticCollection = vscode.languages.createDiagnosticCollection('sindlish');
    context.subscriptions.push(diagnosticCollection);
    const lintDocument = (doc) => {
        if (doc.languageId !== 'sindlish' || doc.uri.scheme !== 'file')
            return;
        diagnosticCollection.delete(doc.uri);
        const lintEngineDir = path.join(context.extensionPath, 'python-engine');
        const linterPath = path.join(lintEngineDir, 'lint.py');
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
        (0, child_process_1.execFile)(pythonCommand, [linterPath, doc.uri.fsPath], { cwd: lintEngineDir }, (error, stdout, stderr) => {
            if (stdout && !stdout.trim().startsWith('OK')) {
                const match = stdout.trim().match(/^(\d+):(.+)/);
                if (match) {
                    const line = Math.max(0, parseInt(match[1]) - 1);
                    const msg = match[2];
                    const range = new vscode.Range(line, 0, line, 100);
                    const diagnostic = new vscode.Diagnostic(range, msg, vscode.DiagnosticSeverity.Error);
                    diagnosticCollection.set(doc.uri, [diagnostic]);
                }
            }
        });
    };
    if (vscode.window.activeTextEditor) {
        lintDocument(vscode.window.activeTextEditor.document);
    }
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(lintDocument));
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(lintDocument));
}
function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
    }
}
//# sourceMappingURL=extension.js.map