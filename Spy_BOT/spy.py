from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
import logging
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define states
CODE = range(1)

# Correct security code
CORRECT_CODE = "anonymous"

# Links to be displayed if the correct code is entered
LINKS = [
    "https://docs.google.com/spreadsheets/d/1SalvGgcrTqUDulcwhBuRmedKP7sbElqcUtaHY4i6qgA/edit?fbclid=IwAR1hhGdN9BUqNhlQxFSpeY9qD73ePAnv1Vsiydmr2VSS5S3039Bze4hbslE&pli=1#gid=1641061892",
    "https://docs.google.com/spreadsheets/d/1FnNM_-aogzOtS6ifsHT1UMoUt-bx_Fbz8FJG-CHEa48/edit#gid=1106603486",
    "https://docs.google.com/spreadsheets/d/1GRsPgR9OKssdN-C4Ft_x-k5HyseN62spap7ywFiMM8k/edit#gid=263690955"
]

# Telegram group link
GROUP_LINK = "https://t.me/+JEZed5ICMD1kYjI1"

# About link
ABOUT_LINK = "https://thredeisacoder.github.io"

# Store message IDs to delete later
user_messages = {}

# Track messages
async def track_message(update: Update, message_id: int):
    chat_id = update.message.chat_id
    if chat_id not in user_messages:
        user_messages[chat_id] = []
    user_messages[chat_id].append(message_id)

# Command /start handler
async def start(update: Update, context: CallbackContext) -> None:
    await track_message(update, update.message.message_id)
    msg = await update.message.reply_text('Hi! I am your bot. How can I help you?')
    await track_message(update, msg.message_id)

# Command /help handler
async def help_command(update: Update, context: CallbackContext) -> None:
    await track_message(update, update.message.message_id)
    help_text = (
        "/start - Start.\n"
        "/help - Displays a list of commands and explanations\n"
        "/access_database - Requires entering a security code to access the link.\n"
        "/cancel - Cancel the current action.\n"
        "/group - Get the link to join our Telegram group.\n"
        "/about - About the developer.\n"
        "/clear - Clear all messages exchanged with the bot."
    )
    msg = await update.message.reply_text(help_text)
    await track_message(update, msg.message_id)

# Command /group handler
async def group_command(update: Update, context: CallbackContext) -> None:
    await track_message(update, update.message.message_id)
    msg = await update.message.reply_text(f'Join our group here: {GROUP_LINK}')
    await track_message(update, msg.message_id)

# Command /about handler
async def about_command(update: Update, context: CallbackContext) -> None:
    await track_message(update, update.message.message_id)
    keyboard = [
        [InlineKeyboardButton("About", url=ABOUT_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text('Click the button below for more information:', reply_markup=reply_markup)
    await track_message(update, msg.message_id)

# Start the authentication process
async def access_database(update: Update, context: CallbackContext) -> int:
    await track_message(update, update.message.message_id)
    msg = await update.message.reply_text('Please enter the security code:')
    await track_message(update, msg.message_id)
    return CODE

# Handle the security code input
async def verify_code(update: Update, context: CallbackContext) -> int:
    await track_message(update, update.message.message_id)
    user_code = update.message.text
    chat_id = update.message.chat_id
    
    if user_code == CORRECT_CODE:
        msg = await update.message.reply_text('Access granted. Here are your links:')
        await track_message(update, msg.message_id)
        for link in LINKS:
            msg = await update.message.reply_text(link)
            await track_message(update, msg.message_id)
        return ConversationHandler.END
    else:
        msg = await update.message.reply_text('Incorrect code. Please try again or type /cancel to stop.')
        await track_message(update, msg.message_id)
        return CODE

# Cancel the authentication process
async def cancel(update: Update, context: CallbackContext) -> int:
    await track_message(update, update.message.message_id)
    msg = await update.message.reply_text('Action canceled.')
    await track_message(update, msg.message_id)
    return ConversationHandler.END

# Cleanup function to delete messages
async def cleanup_all_messages(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                logging.error(f"Error deleting message: {e}")
        del user_messages[chat_id]

# Command /clear handler
async def clear_command(update: Update, context: CallbackContext) -> None:
    await cleanup_all_messages(update, context)
    confirmation_msg = await update.message.reply_text('All messages have been cleared.')
    await asyncio.sleep(10)
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=confirmation_msg.message_id)
    except Exception as e:
        logging.error(f"Error deleting confirmation message: {e}")

def main():
    # Replace 'YOUR_TOKEN' with your actual bot token
    application = Application.builder().token("6828748542:AAEwhxdMfmapbx8aSHBrhm-GI9MBANH9bqU").build()

    # Add handler for the /start command
    application.add_handler(CommandHandler("start", start))

    # Add handler for the /help command
    application.add_handler(CommandHandler("help", help_command))

    # Add handler for the /group command
    application.add_handler(CommandHandler("group", group_command))

    # Add handler for the /about command
    application.add_handler(CommandHandler("about", about_command))

    # Add handler for the /clear command
    application.add_handler(CommandHandler("clear", clear_command))

    # Add handler for the /access_database command using ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('access_database', access_database)],
        states={
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Add handler to track all user messages, including commands
    application.add_handler(MessageHandler(filters.ALL, lambda update, context: track_message(update, update.message.message_id)))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
