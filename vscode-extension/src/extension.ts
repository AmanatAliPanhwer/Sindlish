import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { execFile } from 'child_process';

let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    // 1. Setup Auto-completion and Suggestions natively via built definitions
    const defsPath = path.join(context.extensionPath, 'syntaxes', 'sindlish-definitions.json');
    if (fs.existsSync(defsPath)) {
        const defs = JSON.parse(fs.readFileSync(defsPath, 'utf8'));
        
        const provider = vscode.languages.registerCompletionItemProvider('sindlish', {
            provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
                const completions: vscode.CompletionItem[] = [];
                
                defs.keywords.forEach((kw: string) => {
                    const item = new vscode.CompletionItem(kw, vscode.CompletionItemKind.Keyword);
                    completions.push(item);
                });
                defs.functions.forEach((fn: string) => {
                    const item = new vscode.CompletionItem(fn, vscode.CompletionItemKind.Function);
                    completions.push(item);
                });
                defs.methods.forEach((m: string) => {
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

    const lintDocument = (doc: vscode.TextDocument) => {
        if (doc.languageId !== 'sindlish' || doc.uri.scheme !== 'file') return;

        diagnosticCollection.delete(doc.uri);

        const lintEngineDir = path.join(context.extensionPath, 'python-engine');
        const linterPath = path.join(lintEngineDir, 'lint.py');
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

        execFile(pythonCommand, [linterPath, doc.uri.fsPath], { cwd: lintEngineDir }, (error, stdout, stderr) => {
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

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
    }
}
