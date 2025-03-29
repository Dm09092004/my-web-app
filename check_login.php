<?php
// check_login.php

header('Content-Type: application/json');

// Получаем данные из POST-запроса
$json = file_get_contents('php://input');
$data = json_decode($json, true);

// Проверяем, что все необходимые данные присутствуют
if (!isset($data['username']) || !isset($data['password'])) {
    echo json_encode(['success' => false, 'error' => 'Не все данные предоставлены']);
    exit;
}

$filename = 'users.json';

// Проверяем существование файла с пользователями
if (!file_exists($filename)) {
    echo json_encode(['success' => false, 'error' => 'Файл с пользователями не найден']);
    exit;
}

// Читаем данные пользователей
$users = json_decode(file_get_contents($filename), true);
if (!is_array($users)) {
    echo json_encode(['success' => false, 'error' => 'Ошибка чтения данных пользователей']);
    exit;
}

// Ищем пользователя с таким никнеймом
$foundUser = null;
foreach ($users as $user) {
    if ($user['username'] === $data['username']) {
        $foundUser = $user;
        break;
    }
}

// Проверяем, найден ли пользователь
if (!$foundUser) {
    echo json_encode(['success' => false, 'error' => 'Пользователь не найден']);
    exit;
}

// Проверяем пароль (в реальном проекте используйте password_verify() для хэшированных паролей)
if ($foundUser['password'] !== $data['password']) {
    echo json_encode(['success' => false, 'error' => 'Неверный пароль']);
    exit;
}

// Если все проверки пройдены - успешный вход
echo json_encode([
    'success' => true,
    'user' => [
        'username' => $foundUser['username'],
        'vk_link' => $foundUser['vk_link'],
        'registration_date' => $foundUser['registration_date']
    ]
]);
?>