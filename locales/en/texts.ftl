start-welcome = Hello, { $name }! Let's set up your message forwarding. 
    First, you need a <b>Source Chat</b> (the place I will copy messages from). 
    
    1. Add me to that chat.
    2. Click the button below to select it from your list.

button-source-group = 👥 Select Source Group
button-source-channel = 📢 Select Source Channel

source-success = Awesome! Source chat is successfully linked. 🎯
    
    Now, let's set up the <b>Target Chat</b> (where messages will be forwarded to).
    1. Add me to the target chat.
    2. Select it using the button below.

button-target-group = 👥 Select Target Group
button-target-channel = 📢 Select Target Channel

setup-complete = ✅ All set! 
    Messages from the Source will now be automatically forwarded to the Target chat.

my-header = 📋 Your forwards ({ $count }):

my-item = <b>{ $n }.</b> Source: <code>{ $source_id }</code> → Target: <code>{ $target_id }</code>
    <i>Forward ID: <code>{ $fwd_id }</code></i>

my-empty-text = 📭 You have no forwards yet.
    Press /start to create your first one.

my-empty-button = ➕ Create forward

my-empty-hint = Press /start manually 🙂

my-delete-button = 🗑 Delete

my-delete-confirm = ✅ Yes, delete

my-delete-cancel = ❌ Cancel

my-delete-confirm_text = ⚠️ <b>Delete forward #{ $fwd_id }?</b>
    Source: <code>{ $source_id }</code> → Target: <code>{ $target_id }</code>
    This action cannot be undone.

my-delete-success = ✅ Forward deleted.

my-delete-cancelled = ❌ Cancelled.

my-delete-not-owner = ⛔ This is not your forward.

my-delete-not-found = ⚠️ Forward not found or already deleted.