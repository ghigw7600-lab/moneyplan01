const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// Python Flask 서버 시작
function startPythonServer() {
    const pythonScript = path.join(__dirname, '..', 'web', 'app.py');

    // Windows에서 python 경로 찾기
    const pythonCmd = process.platform === 'win32' ?
        'C:\\Users\\기광우\\AppData\\Local\\Programs\\Python\\Python313\\python.exe' :
        'python3';

    console.log('🐍 Python 서버 시작 중...');
    console.log(`Python 경로: ${pythonCmd}`);
    pythonProcess = spawn(pythonCmd, [pythonScript], {
        cwd: path.join(__dirname, '..', 'web'),
        shell: true
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log(`Python stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python 프로세스 종료: ${code}`);
    });
}

// 메인 윈도우 생성
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: true
        },
        backgroundColor: '#667eea',
        title: '머니플랜01 - AI 투자 분석 시스템',
        autoHideMenuBar: false
    });

    // 메뉴 바 설정
    const template = [
        {
            label: '파일',
            submenu: [
                {
                    label: '새로고침',
                    accelerator: 'F5',
                    click: () => { mainWindow.reload(); }
                },
                { type: 'separator' },
                {
                    label: '종료',
                    accelerator: 'Alt+F4',
                    click: () => { app.quit(); }
                }
            ]
        },
        {
            label: '보기',
            submenu: [
                {
                    label: '전체 화면',
                    accelerator: 'F11',
                    click: () => {
                        mainWindow.setFullScreen(!mainWindow.isFullScreen());
                    }
                },
                { type: 'separator' },
                {
                    label: '개발자 도구',
                    accelerator: 'F12',
                    click: () => { mainWindow.webContents.openDevTools(); }
                }
            ]
        },
        {
            label: '도움말',
            submenu: [
                {
                    label: '정보',
                    click: () => {
                        const { dialog } = require('electron');
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: '머니플랜01',
                            message: '머니플랜01 v1.0.0',
                            detail: 'AI 기반 투자 분석 시스템\n\n본인 및 지인 전용'
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);

    // 3초 후 localhost:5003 로딩 (서버 시작 대기)
    setTimeout(() => {
        mainWindow.loadURL('http://localhost:5003');
    }, 3000);

    // 로딩 중 화면
    const loadingHTML = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    font-family: 'Malgun Gothic', sans-serif;
                    color: white;
                }
                .loading {
                    text-align: center;
                }
                .spinner {
                    width: 60px;
                    height: 60px;
                    border: 5px solid rgba(255,255,255,0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 30px;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                h1 {
                    font-size: 2em;
                    margin-bottom: 10px;
                }
                p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <div class="loading">
                <div class="spinner"></div>
                <h1>🚀 머니플랜01</h1>
                <p>AI 투자 분석 시스템 로딩 중...</p>
            </div>
        </body>
        </html>
    `;
    mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(loadingHTML)}`);

    // 윈도우 닫기 이벤트
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// 앱 준비 완료
app.whenReady().then(() => {
    startPythonServer();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// 모든 윈도우 닫기
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 앱 종료 시 Python 프로세스도 종료
app.on('will-quit', () => {
    if (pythonProcess) {
        console.log('🛑 Python 서버 종료 중...');
        pythonProcess.kill();
    }
});
