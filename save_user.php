<?php
// save_user.php

// Получаем данные из POST-запроса
$json = file_get_contents('php://input');
$data = json_decode($json, true);

// Проверяем, что все необходимые данные присутствуют
if (!isset($data['username']) || !isset($data['password']) || !isset($data['vk_link'])) {
    echo json_encode(['success' => false, 'error' => 'Не все данные предоставлены']);
    exit;
}

// Читаем существующие данные из файла (если есть)
$filename = 'users.json';
$users = [];
if (file_exists($filename)) {
    $users = json_decode(file_get_contents($filename), true);
    if (!is_array($users)) {
        $users = [];
    }
}

// Проверяем, не занят ли никнейм
foreach ($users as $user) {
    if ($user['username'] === $data['username']) {
        echo json_encode(['success' => false, 'error' => 'Этот никнейм уже занят']);
        exit;
    }
}

// Добавляем нового пользователя
$users[] = $data;

// Сохраняем обновленные данные в файл
if (file_put_contents($filename, json_encode($users, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE))) {
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false, 'error' => 'Ошибка при сохранении данных']);
}
?>