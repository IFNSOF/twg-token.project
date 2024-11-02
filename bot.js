const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 3000;

// Замените на ваш токен
const token = '7819136498:AAHO9xsGV83PYIYUwHbBDsItOc72UO_IFv0';
const bot = new TelegramBot(token, { polling: true });

app.use(bodyParser.json());
app.use(express.static('public'));

// Обработка кнопок
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, 'Нажмите кнопку ниже', {
        reply_markup: {
            inline_keyboard: [
                [{ text: 'Кликни меня!', callback_data: 'button_click' }]
            ]
        }
    });
});

// Обработка кликов по кнопкам
bot.on('callback_query', (callbackQuery) => {
    const chatId = callbackQuery.message.chat.id;
    bot.answerCallbackQuery(callbackQuery.id);
    bot.sendMessage(chatId, 'Вы кликнули на кнопку!');
});

// Запуск сервера
app.listen(port, () => {
    console.log(`Сервер слушает на http://localhost:${port}`);
});
