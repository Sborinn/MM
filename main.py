#api.telegram.org/bot8138001996:AAGb9xQ76RnLMhGUmdX1w_W4WOXB5ddYi48/setWebhook?url=https://test-bot-99fg.onrender.com/webhook/8138001996:AAGb9xQ76RnLMhGUmdX1w_W4WOXB5ddYi48
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from Stay_Alive import keep_alive

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler, # Import ConversationHandler
)
from telegram.error import TelegramError # Import TelegramError for error handling
import uuid # Import uuid for generating unique IDs
import sqlite3 # Import sqlite3 for database operations
import datetime # Import datetime for timestamps

# Your bot token
TOKEN = "8138001996:AAGb9xQ76RnLMhGUmdX1w_W4WOXB5ddYi48" # កែសម្រួល Token របស់អ្នក
# Admin chat ID where notifications will be sent
ADMIN_CHAT_ID = 7137869037  # ប្ដូរជាមួយ chat_id របស់ UserAdmin

# Define conversation states for user's account creation
FULL_NAME, PHONE_NUMBER, ACCOUNT_TYPE = range(3)

# Define conversation states for admin's account detail input
ADMIN_ACC_NAME, ADMIN_PASSWORD = range(3, 5) # Removed ADMIN_OTHER_DETAILS state

# Define new conversation states for Deposit/Withdrawal flow
DEPOSIT_WITHDRAW_CHOICE, DEPOSIT_SLIP_INPUT, WITHDRAW_AMOUNT_INPUT, WITHDRAW_PHOTO_INPUT = range(5, 9) # Adjusted range after removing DISPLAY_DEPOSIT_INFO

# Placeholder for Bank Account Image and Wing Number
# IMPORTANT: Replace these with your actual bank account image URLs and Wing money number
BANK_ACCOUNT_IMAGE_URL = "https://photos.app.goo.gl/yJ4jDcuc1Q63mdJ47" # ជំនួសដោយ URL រូបភាពពិតរបស់អ្នក
BANK_ACCOUNT_IMAGE_URL_2 = "https://photos.app.goo.gl/1RxtwFmivuQHYbjD9" # ជំនួសដោយ URL រូបភាពទី2 ពិតរបស់អ្នក
WING_MONEY_NUMBER = "070​ 8500 99"


# Database initialization function
def init_db():
    """Initializes the SQLite database and creates the accounts table if it doesn't exist."""
    try:
        conn = sqlite3.connect('accounts.db')
        cursor = conn.cursor()
        # Modified CREATE TABLE statement to include Telegram user details
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_chat_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                account_type TEXT NOT NULL,
                telegram_first_name TEXT,  -- New column
                telegram_last_name TEXT,   -- New column
                telegram_username TEXT,    -- New column
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Database 'accounts.db' initialized successfully.")
    except sqlite3.Error as e:
        print(f"ERROR: Failed to initialize database: {e}")

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and displays the main menu."""
    menu_keyboard = [["💰 ដក/ដាក់ប្រាក់", "📝 បង្កើតអាខោន"], # Changed this line as requested
                     ["🐓 ព័ត៌មានមាន់", "🆘 ជំនួយ"]]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎉 សូមស្វាគមន៍មកកាន់ M99!", # Welcome message
        reply_markup=reply_markup
    )

# --- User's Account Creation Conversation Handlers ---
async def start_account_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the user's account creation conversation by asking for the full name."""
    await update.message.reply_text("📝 សូមបញ្ចូលឈ្មោះពេញរបស់អ្នក៖")
    return FULL_NAME # Move to the FULL_NAME state

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the full name and asks for the phone number."""
    user_full_name = update.message.text
    if not user_full_name:
        await update.message.reply_text("សូមបញ្ចូលឈ្មោះពេញ។")
        return FULL_NAME # Stay in the same state if input is empty
    context.user_data['full_name'] = user_full_name
    await update.message.reply_text("📞 សូមបញ្ចូលលេខទូរស័ព្ទរបស់អ្នក៖")
    return PHONE_NUMBER # Move to the PHONE_NUMBER state

async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the phone number and asks for the account type."""
    user_phone_number = update.message.text
    if not user_phone_number:
        await update.message.reply_text("សូមបញ្ចូលលេខទូរស័ព្ទ។")
        return PHONE_NUMBER # Stay in the same state if input is empty
    context.user_data['phone_number'] = user_phone_number

    # Create inline keyboard for account type selection
    keyboard = [
        [InlineKeyboardButton("មាន់ជល់រៀល (KHR)", callback_data='type_riel')],
        [InlineKeyboardButton("មាន់ជល់ដុល្លារ (USD)", callback_data='type_usd')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💰 សូមជ្រើសរើសប្រភេទគណនី៖",
        reply_markup=reply_markup
    )
    return ACCOUNT_TYPE # Move to the ACCOUNT_TYPE state

async def get_account_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the account type, sends info to admin, and ends the user's conversation."""
    query = update.callback_query
    await query.answer() # Acknowledge the callback query

    account_type_data = query.data
    if account_type_data == 'type_riel':
        context.user_data['account_type'] = "មាន់ជល់រៀល"
        account_type_display = "មាន់ជល់រៀល (KHR)"
    elif account_type_data == 'type_usd':
        context.user_data['account_type'] = "មាន់ជល់ដុល្លារ"
        account_type_display = "មាន់ជល់ដុល្លារ (USD)"
    else:
        await query.edit_message_text("សូមជ្រើសរើសប្រភេទគណនីត្រឹមត្រូវ។")
        return ACCOUNT_TYPE # Stay in the same state

    # Gather all user data from context.user_data
    full_name = context.user_data.get('full_name', 'N/A')
    phone_number = context.user_data.get('phone_number', 'N/A')
    account_type = context.user_data.get('account_type', 'N/A')

    user_first_name = update.callback_query.from_user.first_name
    user_last_name = update.callback_query.from_user.last_name
    user_username = update.callback_query.from_user.username
    user_chat_id = update.callback_query.message.chat.id # Get the user's chat ID

    # --- Save user account request to accounts.db ---
    try:
        conn = sqlite3.connect('accounts.db')
        cursor = conn.cursor()
        # Updated INSERT statement to include Telegram user details
        cursor.execute(
            "INSERT INTO accounts (user_chat_id, full_name, phone_number, account_type, telegram_first_name, telegram_last_name, telegram_username, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_chat_id, full_name, phone_number, account_type, user_first_name, user_last_name, user_username, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        print(f"DEBUG: Account request from {full_name} saved to accounts.db.")
    except sqlite3.Error as e:
        print(f"ERROR: Failed to save account request to database: {e}")
        await query.message.reply_text("🚫 មានបញ្ហាក្នុងការរក្សាទុកព័ត៌មានរបស់អ្នក។ សូមព្យាយាមម្តងទៀត។")
        context.user_data.clear()
        return ConversationHandler.END
    # --- End Save to DB ---

    # Construct the full name for display to admin
    display_name = user_first_name if user_first_name else "Unnamed User"
    if user_last_name:
        display_name += f" {user_last_name}"

    # Construct the username part for display to admin
    username_str = f" (@{user_username})" if user_username else ""

    # Generate a unique request ID to store the user's data for later retrieval by admin
    request_id = str(uuid.uuid4())
    context.bot_data[request_id] = { # Store in bot_data to be accessible by admin's callback
        'user_chat_id': user_chat_id,
        'full_name': full_name,
        'phone_number': phone_number,
        'account_type': account_type
    }

    # Message to send to admin
    admin_msg = (
        f"📥 ព័ត៌មានបង្កើតអាខោនថ្មីពី {display_name}{username_str}:\n\n"
        f"1️⃣ ឈ្មោះពេញ៖ {full_name}\n"
        f"2️⃣ លេខទូរស័ព្ទ៖ {phone_number}\n"
        f"3️⃣ ប្រភេទគណនី៖ {account_type}\n\n"
        f"សូមចុច 'បង្កើតអោយ' ដើម្បីបញ្ចូលព័ត៌មានគណនី និងផ្ញើទៅភ្ញៀវ។"
    )

    # Buttons for admin to confirm account creation, using the request_id in callback_data
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ បង្កើតអោយ", callback_data=f"acc_confirm_{request_id}")]
    ])

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, reply_markup=buttons)
        await query.edit_message_text(f"✅ បានជ្រើសរើស៖ {account_type_display}\n\nបានទទួលព័ត៌មានបង្កើតអាខោន! សូមរង់ចាំបន្តិច។")
    except TelegramError as e:
        print(f"ERROR: Could not send account creation info to admin: {e}")
        await query.edit_message_text("មានបញ្ហាក្នុងការផ្ញើព័ត៌មានរបស់អ្នកទៅ Admin។ សូមព្យាយាមម្តងទៀត។")

    return ConversationHandler.END # End the user's conversation

async def cancel_account_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the user's conversation."""
    await update.message.reply_text(
        "🚫 ការបង្កើតអាខោនត្រូវបានលុបចោល។",
        reply_markup=ReplyKeyboardMarkup([["💰 ដក/ដាក់ប្រាក់", "📝 បង្កើតអាខោន"], # Adjusted fallback menu
                                         ["🐓 ព័ត៌មានមាន់", "🆘 ជំនួយ"]], resize_keyboard=True)
    )
    # Clear user_data for the conversation
    context.user_data.clear()
    return ConversationHandler.END

# --- Admin's Account Detail Input Conversation Handlers ---
async def admin_start_account_detail_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the admin's conversation to input account details."""
    print(f"DEBUG: admin_start_account_detail_input triggered. Callback data: {update.callback_query.data}") # Debug print
    query = update.callback_query
    await query.answer()
    print("DEBUG: Callback query answered.") # Debug print

    # Fix: Correctly extract the request_id
    # The callback data is like "acc_confirm_UUID", so splitting by "_" will give ["acc", "confirm", "UUID"]
    # We need the last part, which is the UUID.
    callback_parts = query.data.split('_')
    if len(callback_parts) > 2 and callback_parts[0] == 'acc' and callback_parts[1] == 'confirm':
        request_id = callback_parts[2]
    else:
        # Fallback for unexpected callback data, though it should ideally not happen with the current setup
        print(f"ERROR: Unexpected callback data format: {query.data}")
        await query.edit_message_text("🚫 កំហុសក្នុងការដំណើរការសំណើ។ ទម្រង់ទិន្នន័យមិនត្រឹមត្រូវ។")
        return ConversationHandler.END

    request_data = context.bot_data.get(request_id, None)
    print(f"DEBUG: Retrieved request_id: {request_id}, request_data found: {request_data is not None}") # Debug print

    if not request_data:
        try:
            await query.edit_message_text("🚫 សំណើបង្កើតអាខោននេះមិនត្រូវបានរកឃើញទេ ឬត្រូវបានដំណើរការរួចហើយ។")
        except TelegramError as e:
            print(f"ERROR: Could not edit admin message for missing request data: {e}")
        return ConversationHandler.END # End admin's conversation if data not found

    # Store the request_data in admin's user_data for this specific conversation
    context.user_data['admin_processing_request_id'] = request_id
    context.user_data['user_request_data'] = request_data

    # Prompt for Account Name
    try:
        await query.edit_message_text(
            f"✅ ទទួលសំណើបង្កើតអាខោនសម្រាប់ {request_data['full_name']} ({request_data['account_type']})។\n\n"
            f"1️⃣ សូមបញ្ចូលឈ្មោះគណនី (username)៖"
        )
        print("DEBUG: Admin prompted for account name.") # Debug print
    except TelegramError as e:
        print(f"ERROR: Could not edit admin message to prompt for account name: {e}")
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="មានបញ្ហាក្នុងការចាប់ផ្តើមដំណើរការបញ្ចូលព័ត៌មាន។ សូមព្យាយាមម្តងទៀត។")

    return ADMIN_ACC_NAME # Move to the ADMIN_ACC_NAME state

async def admin_get_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the account name from admin and asks for the password."""
    print(f"DEBUG: admin_get_account_name triggered. Admin input: {update.message.text}") # Debug print
    admin_account_name = update.message.text
    if not admin_account_name:
        await update.message.reply_text("សូមបញ្ចូលឈ្មោះគណនី។")
        return ADMIN_ACC_NAME

    context.user_data['admin_account_name'] = admin_account_name
    await update.message.reply_text("2️⃣ សូមបញ្ចូលពាក្យសម្ងាត់ (password)៖")
    return ADMIN_PASSWORD # Move to the ADMIN_PASSWORD state

async def admin_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receives the password from admin, sets fixed other details,
    sends confirmation to user, and ends conversation.
    """
    print(f"DEBUG: admin_get_password triggered. Admin input: {update.message.text}") # Debug print
    admin_password = update.message.text
    if not admin_password:
        await update.message.reply_text("សូមបញ្ចូលពាក្យសម្ងាត់។")
        return ADMIN_PASSWORD

    context.user_data['admin_password'] = admin_password
    # Fixed other details as requested
    admin_other_details = "https://m99.ink" 

    request_data = context.user_data.get('user_request_data')
    if not request_data:
        await update.message.reply_text("🚫 កំហុស៖ ព័ត៌មានសំណើមិនត្រូវបានរកឃើញទេ។ សូមចាប់ផ្តើមឡើងវិញ។")
        context.user_data.clear()
        return ConversationHandler.END

    user_chat_id = request_data['user_chat_id']
    full_name = request_data['full_name']
    phone_number = request_data['phone_number']
    account_type = request_data['account_type']
    admin_account_name = context.user_data.get('admin_account_name', 'N/A')
    admin_password = context.user_data.get('admin_password', 'N/A')

    # Construct the final confirmation message for the user, including admin's input
    user_confirmation_msg = (
        f"✅ Admin បានបង្កើតអាខោនរបស់អ្នករួចហើយ! 🎉 សូមពិនិត្យ។\n\n"
        f"ព័ត៌មានលម្អិតគណនីរបស់អ្នក:\n" # Corrected typo: ព័រត៌មានលម្អិត -> ព័ត៌មានលម្អិត
        f"  ➡️ ឈ្មោះពេញ: {full_name}\n"
        f"  ➡️ លេខទូរស័ព្ទ: {phone_number}\n"
        f"  ➡️ ប្រភេទគណនី: {account_type}\n\n"
        f"ព័ត៌មានគណនីដែល Admin បានផ្តល់:\n"
        f"  ➡️ ឈ្មោះគណនី: `{admin_account_name}`\n"
        f"  ➡️ ពាក្យសម្ងាត់: `{admin_password}`\n"
        f"  ➡️ វេបសាយ: {admin_other_details}\n\n"
        f"ប្រសិនបើមានចម្ងល់ សូមទាក់ទងមកកាន់តេលេក្រាមផ្លូវការ: @CSM99Company។"
    )

    print(f"DEBUG: Admin received account details for user {user_chat_id}. Sending confirmation...")
    try:
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=user_confirmation_msg,
            parse_mode='Markdown' # Use Markdown to correctly format backticks for account name/password
        )
        await update.message.reply_text("✅ ព័ត៌មានគណនីត្រូវបានផ្ញើទៅភ្ញៀវហើយ។")
        print(f"DEBUG: Successfully sent account details to user {user_chat_id}.")
    except TelegramError as e:
        print(f"ERROR: Could not send account details to user {user_chat_id}: {e}")
        await update.message.reply_text(f"🚫 កំហុសក្នុងការផ្ញើព័ត៌មានទៅភ្ញៀវ៖ {e}\nសូមព្យាយាមម្តងទៀត។")

    # Clean up admin's user_data for this conversation
    context.user_data.clear()
    # Remove the request from bot_data as it's now processed
    # This ensures that an admin cannot process the same request_id twice.
    if 'admin_processing_request_id' in context.user_data: # Check if key exists before popping
        context.bot_data.pop(context.user_data['admin_processing_request_id'], None)

    return ConversationHandler.END # End the admin's conversation

async def admin_cancel_account_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the admin's conversation for account detail input."""
    print("DEBUG: admin_cancel_account_creation triggered.") # Debug print
    await update.message.reply_text("🚫 ការបញ្ចូលព័ត៌មានគណនីត្រូវបានលុបចោល។")
    context.user_data.clear() # Clear admin's user_data
    return ConversationHandler.END

# --- Deposit/Withdrawal Conversation Handlers ---
async def start_deposit_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a menu for Deposit/Withdraw options."""
    keyboard = [
        [InlineKeyboardButton("ដាក់ប្រាក់ (Deposit)", callback_data='action_deposit')],
        [InlineKeyboardButton("ដកប្រាក់ (Withdraw)", callback_data='action_withdraw')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("💵 សូមជ្រើសរើសសេវាកម្ម៖", reply_markup=reply_markup)
    return DEPOSIT_WITHDRAW_CHOICE

async def handle_deposit_withdraw_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the choice between Deposit and Withdraw."""
    query = update.callback_query
    await query.answer()

    if query.data == 'action_deposit':
        user_chat_id = query.message.chat.id

        deposit_message = (
            "💵 សូមផ្ញើប្រាក់ទៅកាន់គណនីធនាគារខាងក្រោម៖\n"
            f"លេខវីងវេរលុយ: `{WING_MONEY_NUMBER}`\n\n"
            "បន្ទាប់ពីផ្ទេរប្រាក់រួច សូមផ្ញើវិក្កយបត្រផ្ទេរប្រាក់ (ជារូបភាព)។"
        )

        try:
            # Send the first bank account image
            await context.bot.send_photo(
                chat_id=user_chat_id,
                photo=BANK_ACCOUNT_IMAGE_URL,
                caption=""
            )
            # Send the second bank account image
            await context.bot.send_photo(
                chat_id=user_chat_id,
                photo=BANK_ACCOUNT_IMAGE_URL_2,
                caption=""
            )
            # Send the text message with Wing details and instructions
            await context.bot.send_message(
                chat_id=user_chat_id,
                text=deposit_message,
                parse_mode='Markdown'
            )
        except TelegramError as e:
            print(f"ERROR: Could not send deposit info to user {user_chat_id}: {e}")
            # If sending images fails, at least inform the user to send the slip
            await query.edit_message_text("មានបញ្ហាក្នុងការបង្ហាញព័ត៌មានដាក់ប្រាក់។ សូមផ្ញើវិក្កយបត្រផ្ទេរប្រាក់ (ជារូបភាព)។")
            return DEPOSIT_SLIP_INPUT # Still transition to this state to receive slip

        # After sending images and info, inform user to send slip
        await query.edit_message_text("✅ ព័ត៌មានដាក់ប្រាក់ត្រូវបានផ្ញើ។ ឥឡូវសូមផ្ញើវិក្កយបត្រផ្ទេរប្រាក់ (ជារូបភាព)។")
        return DEPOSIT_SLIP_INPUT # Transition to state that expects a photo
    elif query.data == 'action_withdraw':
        await query.edit_message_text("💸 សូមវាយបញ្ចូលចំនួនទឹកប្រាក់ដែលអ្នកចង់ដក (ឧទាហរណ៍ : 10$)៖")
        return WITHDRAW_AMOUNT_INPUT
    return ConversationHandler.END # Fallback in case of unexpected callback_data

async def show_deposit_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /depositinfo command and displays bank account images and Wing money number."""
    user_chat_id = update.effective_chat.id

    deposit_message = (
        "💵 សូមផ្ញើប្រាក់ទៅកាន់គណនីធនាគារខាងក្រោម៖\n"
        f"លេខ Wing: `{WING_MONEY_NUMBER}`\n\n"
        "បន្ទាប់ពីផ្ទេរប្រាក់រួច សូមផ្ញើ slip ផ្ទេរប្រាក់ (ជារូបភាព) នៅក្នុងសេវាកម្ម 'ដាក់ប្រាក់'។"
    )

    try:
        # Send the first bank account image
        await context.bot.send_photo(
            chat_id=user_chat_id,
            photo=BANK_ACCOUNT_IMAGE_URL, # នេះគឺជាកន្លែងដែល Bot ព្យាយាមផ្ញើរូបភាព
           # Caption for the first image
        )
        # Send the second bank account image
        await context.bot.send_photo(
            chat_id=user_chat_id,
            photo=BANK_ACCOUNT_IMAGE_URL_2, # នេះគឺជាកន្លែងដែល Bot ព្យាយាមផ្ញើរូបភាព
            # Caption for the second image
        )
        # Send the text message with Wing details and instructions
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=deposit_message,
            parse_mode='Markdown'
        )
    except TelegramError as e:
        print(f"ERROR: Could not send deposit info to user {user_chat_id}: {e}")
        await context.bot.send_message(chat_id=user_chat_id, text="មានបញ្ហាក្នុងការបង្ហាញព័ត៌មានដាក់ប្រាក់។ សូមព្យាយាមម្តងទៀត។")


async def process_deposit_slip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives deposit slip (photo) and forwards it to admin."""
    if update.message.photo:
        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username

        display_name = user_first_name if user_first_name else "Unnamed User"
        if user_last_name:
            display_name += f" {user_last_name}"
        username_str = f" (@{user_username})" if user_username else ""

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ទទួលប្រាក់", callback_data=f"confirm_{update.message.chat.id}"),
                InlineKeyboardButton("❌ បដិសេធ", callback_data=f"reject_{update.message.chat.id}")
            ]
        ])
        # Updated caption for deposit slip
        caption = f"📸 Slip ដាក់ប្រាក់ពី {display_name}{username_str} \n\nចុច \"ទទួលប្រាក់\" ឬ \"បដិសេធ\" ខាងក្រោម:"

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=buttons
            )
            await update.message.reply_text("✅ បានទទួល Slip របស់អ្នក... សូមរង់ចាំបន្តិច")
        except TelegramError as e:
            print(f"ERROR: Could not send deposit slip to admin: {e}")
            await update.message.reply_text("មានបញ្ហាក្នុងការផ្ញើ Slip របស់អ្នកទៅ Admin។ សូមព្យាយាមម្តងទៀត។")
    else:
        await update.message.reply_text("📸 សូមផ្ញើក្រដាសវិក្កយបត្រផ្ទេរប្រាក់ (ជារូបភាព)។")
        return DEPOSIT_SLIP_INPUT # Stay in this state until a photo is received
    return ConversationHandler.END

async def get_withdrawal_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives withdrawal amount and asks for a photo."""
    amount = update.message.text
    if not amount:
        await update.message.reply_text("សូមវាយបញ្ចូលចំនួនទឹកប្រាក់។")
        return WITHDRAW_AMOUNT_INPUT

    context.user_data['withdrawal_amount'] = amount
    await update.message.reply_text("📸 សូមផ្ញើ QR Code ដើម្បីធ្វើការដកប្រាក់ជូនបង (QR Code ធនាគារ ឬលេខគណនី)៖")
    return WITHDRAW_PHOTO_INPUT

async def process_withdrawal_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives withdrawal photo and forwards details to admin."""
    if update.message.photo:
        amount = context.user_data.get('withdrawal_amount', 'មិនបានបញ្ជាក់')

        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username

        display_name = user_first_name if user_first_name else "Unnamed User"
        if user_last_name:
            display_name += f" {user_last_name}"
        username_str = f" (@{user_username})" if user_username else ""

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ទទួលសំណើដកប្រាក់", callback_data=f"withdraw_confirm_{update.message.chat.id}"),
                InlineKeyboardButton("❌ បដិសេធសំណើដកប្រាក់", callback_data=f"withdraw_reject_{update.message.chat.id}")
            ]
        ])

        caption = (
            f"💸 សំណើដកប្រាក់ពី {display_name}{username_str}\n"
            f"ចំនួនទឹកប្រាក់: {amount}\n\n"
            f"ចុច \"ទទួលសំណើដកប្រាក់\" ឬ \"បដិសេធសំណើដកប្រាក់\" ខាងក្រោម:"
        )

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=buttons
            )
            await update.message.reply_text("✅ បានទទួលសំណើដកប្រាក់របស់អ្នក... សូមរង់ចាំបន្តិច")
        except TelegramError as e:
            print(f"ERROR: Could not send withdrawal request to admin: {e}")
            await update.message.reply_text("មានបញ្ហាក្នុងការផ្ញើសំណើដកប្រាក់របស់អ្នកទៅ Admin។ សូមព្យាយាមម្តងទៀត។")
    else:
        await update.message.reply_text("📸 សូមផ្ញើរូបភាពដែលពាក់ព័ន្ធនឹងការដកប្រាក់។")
        return WITHDRAW_PHOTO_INPUT # Stay in this state until a photo is received

    context.user_data.clear() # Clear user_data for withdrawal conversation
    return ConversationHandler.END

async def cancel_deposit_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the deposit/withdraw conversation."""
    await update.message.reply_text(
        "🚫 សេវាកម្មដក/ដាក់ប្រាក់ត្រូវបានលុបចោល។",
        reply_markup=ReplyKeyboardMarkup([["💰 ដក/ដាក់ប្រាក់", "📝 បង្កើតអាខោន"],
                                         ["🐓 ព័ត៌មានមាន់", "🆘 ជំនួយ"]], resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END


# --- General Message Handler (for non-conversation text) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles general text messages that are not part of any ongoing conversation."""
    text = update.message.text.lower()
    reply = ""

    if "មាន់" in text:
        # Updated "ព័ត៌មានមាន់" section
        reply = (
            "📢 ព័ត៌មានមាន់ជល់ថ្មីៗ (សម្រាប់អ្នកភ្នាល់)\n"
            "🔥 ប្រភេទមាន់ពេញនិយមនៅ M99 ថ្ងៃនេះ!\n"
            "✔ មាន់ខ្មៅភ្លើង – ស្ទាត់ជំនាញការវាយលឿន, អាចវាយចំចិត្តប្រូម៉ូទ័រ\n"
            "✔ មាន់សចំណុច – ស៊ាំនឹងការវាយធ្ងន់, ស័ក្តិសមសម្រាប់ភ្នាល់យូរ\n"
            "✔ មាន់យីហោ – ល្បឿនខ្ពស់, ប្រយុទ្ធតាមរយៈការវាយរហ័ស\n\n"
            "📈 ការវិភាគថ្ងៃនេះ:\n"
            ".មាន់ខ្មៅភ្លើងមានអត្រាឈ្នះ 70% ក្នុង ៥វគ្គចុងក្រោយ\n"
            ".មាន់សចំណុចល្អសម្រាប់ភ្នាល់ វគ្គវែង (ល្បឿនយឺត តែអស់ពីកម្លាំង)\n\n"
            "🎯 របៀបជ្រើសរើសមាន់ឈ្នះ (សម្រាប់អ្នកចាប់ផ្តើម)\n"
            "✔ សង្កេតមាន់មុនវគ្គ – មើលស្ទីលវាយ, កម្លាំងជើង\n"
            "✔ វិភាគរូបរាង – មាន់ល្អត្រូវមានរូបរាងស្គម, ភ្នែកភ្លឺ\n"
            "✔ ពិនិត្យប្រវត្តិ – មាន់ដែលឈ្នះ ៣វគ្គជាប់ៗមានឱកាសឈ្នះខ្ពស់"
        )
    elif "ជំនួយ" in text:
        reply = "🆘 សូមទំនាក់ទំនងតេលេក្រាមផ្លូវកា CS: @CSM99Company"
    else:
        # If none of the keywords match, it's an unhandled message
        reply = "ខ្ញុំមិនទាន់យល់ពីសំណួររបស់អ្នកទេ។ សូមជ្រើសរើសពី Menu ឬសួរខ្ញុំផ្សេងទៀត។"

    await update.message.reply_text(reply)

# --- General Photo Forwarding Handler (This will catch photos not part of any specific conversation) ---
# Note: The specific photo handling for deposit/withdraw are now within their respective conversation handlers.
# This general handler will act as a fallback for any other photos sent by the user.
async def forward_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards any unhandled photo messages to the admin."""
    if update.message.photo:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ទទួល", callback_data=f"generic_confirm_{update.message.chat.id}"),
                InlineKeyboardButton("❌ បដិសេធ", callback_data=f"generic_reject_{update.message.chat.id}")
            ]
        ])

        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username

        display_name = user_first_name if user_first_name else "Unnamed User"
        if user_last_name:
            display_name += f" {user_last_name}"
        username_str = f" (@{user_username})" if user_username else ""

        caption = f"📸 រូបភាពពី {display_name}{username_str} \n\nចុច \"ទទួល\" ឬ \"បដិសេធ\" ខាងក្រោម:"

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=buttons
            )
            await update.message.reply_text("✅ បានទទួលរូបភាពរបស់អ្នក... សូមរង់ចាំបន្តិច")
        except TelegramError as e:
            print(f"ERROR: Could not send photo to admin: {e}")
            await update.message.reply_text("មានបញ្ហាក្នុងការផ្ញើរូបភាពរបស់អ្នកទៅ Admin។ សូមព្យាយាមម្តងទៀត។")
    else:
        # This part should ideally not be reached if filters.PHOTO is used, but as a safeguard:
        await update.message.reply_text("📸 សូមផ្ញើរូបភាព។")


# --- Callback Handler for General Admin Actions (Payment related and Generic Photo) ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline keyboard button callbacks for payment confirmations/rejections and generic photo actions."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("confirm_"): # For Deposit confirmation
        user_chat_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="✅ ទឹកប្រាក់បានដាក់ចូលគណនីរបស់អ្នករួចរាល់! 🎉 សូមអរគុណ។"
            )
            print(f"DEBUG: Sent payment confirmation to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send payment confirmation to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="✅ដាក់ប្រាក់ជូនរួចរាល់។")

    elif query.data.startswith("reject_"): # For Deposit rejection
        user_chat_id = int(query.data.split("_")[1])
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="❌ សូមអភ័យទោស Slip របស់អ្នកត្រូវបានបដិសេធ។ សូមពិនិត្យ និងផ្ញើថ្មីម្តងទៀត។"
            )
            print(f"DEBUG: Sent payment rejection to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send payment rejection to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="❌ Slip ត្រូវបានបដិសេធ។")

    elif query.data.startswith("withdraw_confirm_"): # For Withdrawal confirmation
        user_chat_id = int(query.data.split("_")[2]) # Note: split by _ will result in ['withdraw', 'confirm', 'chat_id']
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="✅ Admin បានទទួលសំណើដកប្រាក់របស់អ្នកហើយ! 🎉 សូមរង់ចាំការដំណើរការ។"
            )
            print(f"DEBUG: Sent withdrawal confirmation to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send withdrawal confirmation to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="✅ សំណើដកប្រាក់ត្រូវបានទទួលរួច។ 🎉")

    elif query.data.startswith("withdraw_reject_"): # For Withdrawal rejection
        user_chat_id = int(query.data.split("_")[2]) # Note: split by _ will result in ['withdraw', 'reject', 'chat_id']
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="❌ សូមអភ័យទោស សំណើដកប្រាក់របស់អ្នកត្រូវបានបដិសេធ។ សូមពិនិត្យ និងផ្ញើថ្មីម្តងទៀត។"
            )
            print(f"DEBUG: Sent withdrawal rejection to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send withdrawal rejection to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="❌ សំណើដកប្រាក់ត្រូវបានបដិសេធ។")

    elif query.data.startswith("generic_confirm_"): # For generic photo confirmation
        user_chat_id = int(query.data.split("_")[2])
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="✅ កំពុងពិនិត្យរូបភាពរបស់អ្នកហើយ។"
            )
            print(f"DEBUG: Sent generic photo confirmation to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send generic photo confirmation to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="✅ រូបភាពត្រូវបានទទួល។")

    elif query.data.startswith("generic_reject_"): # For generic photo rejection
        user_chat_id = int(query.data.split("_")[2])
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="❌ Admin បានបដិសេធរូបភាពរបស់អ្នក។"
            )
            print(f"DEBUG: Sent generic photo rejection to user chat ID: {user_chat_id}")
        except TelegramError as e:
            print(f"ERROR: Could not send generic photo rejection to {user_chat_id}: {e}")
        await query.edit_message_caption(caption="❌ រូបភាពត្រូវបានបដិសេធ។")


# Main entry point for the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Initialize the database
    init_db()

    # Conversation handler for user's account creation process
    user_account_creation_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("📝 បង្កើតអាខោន"), start_account_creation)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_number)],
            ACCOUNT_TYPE: [CallbackQueryHandler(get_account_type, pattern='^(type_riel|type_usd)$')],
        },
        fallbacks=[CommandHandler("cancel", cancel_account_creation),
                   MessageHandler(filters.ALL & ~filters.COMMAND, cancel_account_creation)],
    )

    # Conversation handler for admin's account detail input process
    admin_account_input_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_start_account_detail_input, pattern=r'^acc_confirm_[0-9a-fA-F-]+$')],
        states={
            ADMIN_ACC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_account_name)],
            ADMIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_password)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel_account_creation)],
        allow_reentry=True
    )

    # Conversation handler for Deposit/Withdrawal flow
    deposit_withdraw_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("💰 ដក/ដាក់ប្រាក់"), start_deposit_withdraw)],
        states={
            DEPOSIT_WITHDRAW_CHOICE: [CallbackQueryHandler(handle_deposit_withdraw_choice, pattern='^(action_deposit|action_withdraw)$')],
            DEPOSIT_SLIP_INPUT: [MessageHandler(filters.PHOTO, process_deposit_slip)],
            WITHDRAW_AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdrawal_amount)],
            WITHDRAW_PHOTO_INPUT: [MessageHandler(filters.PHOTO, process_withdrawal_details)],
        },
        fallbacks=[CommandHandler("cancel", cancel_deposit_withdraw),
                   MessageHandler(filters.TEXT & ~filters.COMMAND, cancel_deposit_withdraw)], # Allow text to cancel
    )


    # Add handlers to the application
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("depositinfo", show_deposit_info)) # Add the new command handler for deposit info
    app.add_handler(user_account_creation_conv_handler)
    app.add_handler(admin_account_input_conv_handler)
    app.add_handler(deposit_withdraw_conv_handler) # Add the new deposit/withdraw conversation handler

    # IMPORTANT: The order of handlers matters. General handlers should come after specific ones.
    # General message handler (catches text messages not handled by conversations/commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # General photo handler (catches photo messages not handled by conversations)
    app.add_handler(MessageHandler(filters.PHOTO, forward_photo))
    # General callback handler (catches callbacks not handled by conversations)
    app.add_handler(CallbackQueryHandler(button_callback)) 

    print("🤖 Bot កំពុងដំណើរការ...") # Bot running message
    app.run_polling()
