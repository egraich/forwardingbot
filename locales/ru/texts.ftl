start-welcome = Привет, <b>{ $name }</b>! 👋
    Давай настроим пересылку сообщений.
    
    Сначала нужен <b>Чат-источник (Source)</b> — откуда я буду забирать сообщения.
    
    1. Добавь меня в этот чат или канал.
    2. Нажми на кнопку ниже, чтобы выбрать его.

button-source-group = 👥 Выбрать группу-источник
button-source-channel = 📢 Выбрать канал-источник

source-success = Отлично! Чат-источник привязан. 🎯
    
    Теперь нужен <b>Target-чат</b> — куда я буду пересылать сообщения.
    1. Добавь меня в target-чат/канал.
    2. Выбери его, нажав на кнопку ниже.

button-target-group = 👥 Выбрать Target-группу
button-target-channel = 📢 Выбрать Target-канал

setup-complete = ✅ <b>Всё готово!</b> 
    Связка успешно создана. Теперь новые сообщения будут автоматически пересылаться.

my-header = 📋 Твои пересылки ({ $count }):

my-item = <b>{ $n }.</b> Source: <code>{ $source_id }</code> → Target: <code>{ $target_id }</code>
    <i>ID связки: <code>{ $fwd_id }</code></i>

my-empty-text = 📭 У тебя пока нет пересылок.
    Нажми /start, чтобы создать первую.

my-empty-button = ➕ Создать пересылку

my-empty-hint = Нажми /start вручную 🙂

my-delete-button = 🗑 Удалить

my-delete-confirm = ✅ Да, удалить

my-delete-cancel = ❌ Отмена

my-delete-confirm_text = ⚠️ <b>Удалить пересылку #{ $fwd_id }?</b>
    Source: <code>{ $source_id }</code> → Target: <code>{ $target_id }</code>
    Действие нельзя отменить.

my-delete-success = ✅ Пересылка удалена.

my-delete-cancelled = ❌ Отменено.

my-delete-not-owner = ⛔ Это не твоя пересылка.

my-delete-not-found = ⚠️ Пересылка не найдена или уже удалена.