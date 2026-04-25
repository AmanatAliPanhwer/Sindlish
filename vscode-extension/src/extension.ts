import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    // Server implementation path
    const serverModule = context.asAbsolutePath(path.join('server', 'server.py'));

    // Server options for Python Language Server
    const serverOptions: ServerOptions = {
        run: { command: 'python', args: [serverModule] },
        debug: { command: 'python', args: [serverModule] }
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'sindlish' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.sd')
        }
    };

    // Setup Diagnostic System
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('sindlish');
    context.subscriptions.push(diagnosticCollection);

    // Create and start the client
    client = new LanguageClient(
        'sindlishLanguageServer',
        'Sindlish Language Server',
        serverOptions,
        {
            ...clientOptions,
            traceOutputChannel: vscode.window.createOutputChannel('Sindlish Language Server Trace')
        }
    );

    // Explicitly listen to publishDiagnostics to update the collection
    client.onNotification('textDocument/publishDiagnostics', (params: any) => {
        console.log('PublishDiagnostics Notification Received:', params);
        const uri = vscode.Uri.parse(params.uri);
        const diagnostics = params.diagnostics.map((d: any) => new vscode.Diagnostic(
            new vscode.Range(d.range.start.line, d.range.start.character, d.range.end.line, d.range.end.character),
            d.message,
            vscode.DiagnosticSeverity.Error
        ));
        diagnosticCollection.set(uri, diagnostics);
    });

    // Status Bar Item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(sync~spin) Sindlish LSP";
    statusBarItem.tooltip = "Sindlish Language Server is running";
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    client.start().then(() => {
        statusBarItem.text = "$(check) Sindlish LSP";
    }).catch(() => {
        statusBarItem.text = "$(error) Sindlish LSP";
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    });
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
