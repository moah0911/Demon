import * as vscode from 'vscode';
import * as path from 'path';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('Activating Demon Language Extension');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('demon.restart', () => {
            restartLanguageServer(context);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('demon.typeCheck', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'demon') {
                client.sendRequest('workspace/executeCommand', {
                    command: 'demon.typeCheck',
                    arguments: [editor.document.uri.toString()]
                });
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('demon.format', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'demon') {
                client.sendRequest('workspace/executeCommand', {
                    command: 'demon.format',
                    arguments: [editor.document.uri.toString()]
                });
            }
        })
    );

    // Start language server
    startLanguageServer(context);
}

function startLanguageServer(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('demon');
    
    if (!config.get('languageServer.enable')) {
        return;
    }

    // Server options
    const serverOptions: ServerOptions = {
        run: {
            command: 'python',
            args: [path.join(__dirname, '..', '..', '..', 'demon_cli.py'), '--ide'],
            options: {
                cwd: path.join(__dirname, '..', '..', '..')
            }
        },
        debug: {
            command: 'python',
            args: [path.join(__dirname, '..', '..', '..', 'demon_cli.py'), '--ide', '--debug'],
            options: {
                cwd: path.join(__dirname, '..', '..', '..')
            }
        }
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'demon' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.demon')
        }
    };

    // Create and start client
    client = new LanguageClient(
        'demonLanguageServer',
        'Demon Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client
    const disposable = client.start();
    
    // Push client to subscriptions
    context.subscriptions.push(disposable);
    
    console.log('Demon Language Server started');
}

function restartLanguageServer(context: vscode.ExtensionContext) {
    if (client) {
        client.stop().then(() => {
            startLanguageServer(context);
            vscode.window.showInformationMessage('Demon Language Server restarted');
        });
    } else {
        startLanguageServer(context);
        vscode.window.showInformationMessage('Demon Language Server started');
    }
}

export function deactivate(): Thenable<void> | undefined {
    if (client) {
        return client.stop();
    }
    return undefined;
}