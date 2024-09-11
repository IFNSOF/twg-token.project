const balanceElement = document.getElementById('balance');
const playButton = document.getElementById('play');

let balance = 0;

const supabaseUrl = 'https://whvhlqsyjttwpzdlzofy.supabase.co'; // Замените на ваш URL
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndodmhscXN5anR0d3B6ZGx6b2Z5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYwNjAyOTIsImV4cCI6MjA0MTYzNjI5Mn0.Ru240VVmhYh-HAvCiVBCHW9R6HT1TqV1rqpcT5VP7vI'; // Замените на ваш API-ключ

// Инициализация Supabase
const supabase = supabase.createClient(supabaseUrl, supabaseKey);

// Создание функции для сохранения баланса
async function saveBalance() {
  const userId = "ваш_идентификатор_пользователя"; // Используйте уникальный ID для пользователя
  const { error } = await supabase
    .from('user_balances')
    .upsert({ user_id: userId, balance });
  if (error) {
    console.error('Ошибка сохранения баланса:', error);
  }
}

// Создание функции для загрузки баланса
async function loadBalance() {
  const userId = "ваш_идентификатор_пользователя"; 
  const { data, error } = await supabase
    .from('user_balances')
    .select('balance')
    .eq('user_id', userId);
  if (error) {
    console.error('Ошибка загрузки баланса:', error);
    return;
  }
  balance = data[0] ? data[0].balance : 0;
  balanceElement.textContent = `Баланс: ${balance}`;
}

// Функция игры
function playGame() {
  // ... ваш код логики игры ...
  // Обновить баланс
  balance = новый баланс;
  balanceElement.textContent = `Баланс: ${balance}`;
  // Сохранить баланс в Supabase
  saveBalance();
}

playButton.addEventListener('click', playGame);

// Загрузить начальный баланс при загрузке страницы
loadBalance(); 
