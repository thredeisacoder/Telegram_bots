from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Khai báo các bước của ConversationHandler
CODE = range(1)

# Mã bảo mật đúng
CORRECT_CODE = "anonymous"

# Các đường link sẽ hiển thị nếu mã bảo mật đúng
LINKS = [
    "https://docs.google.com/spreadsheets/d/1SalvGgcrTqUDulcwhBuRmedKP7sbElqcUtaHY4i6qgA/edit?fbclid=IwAR1hhGdN9BUqNhlQxFSpeY9qD73ePAnv1Vsiydmr2VSS5S3039Bze4hbslE&pli=1#gid=1641061892",
    "https://docs.google.com/spreadsheets/d/1FnNM_-aogzOtS6ifsHT1UMoUt-bx_Fbz8FJG-CHEa48/edit#gid=1106603486",
    "https://docs.google.com/spreadsheets/d/1GRsPgR9OKssdN-C4Ft_x-k5HyseN62spap7ywFiMM8k/edit#gid=263690955"
]

# Đường link đến nhóm Telegram
GROUP_LINK = "https://t.me/+JEZed5ICMD1kYjI1"

# Đường link cho lệnh /about
ABOUT_LINK = "https://thredeisacoder.github.io"

# Hàm xử lý lệnh /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! I am your bot. How can I help you?')

# Hàm xử lý lệnh /help
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "/start - Khởi động bot và nhận thông báo chào mừng\n"
        "/help - Hiển thị danh sách các lệnh và giải thích\n"
        "/access_database - Yêu cầu nhập mã bảo mật để truy cập đường link\n"
        "/cancel - Hủy bỏ hành động hiện tại\n"
        "/group - Nhận đường link để truy cập nhóm Telegram\n"
        "/about - Hiển thị thông tin về bot và dẫn đến trang web của bạn"
    )
    await update.message.reply_text(help_text)

# Hàm xử lý lệnh /group
async def group_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(f'Join our group here: {GROUP_LINK}')

# Hàm xử lý lệnh /about
async def about_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("About", url=ABOUT_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Click the button below for more information:', reply_markup=reply_markup)

# Hàm bắt đầu quy trình xác thực
async def access_database(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Please enter the security code:')
    return CODE

# Hàm xử lý mã bảo mật
async def verify_code(update: Update, context: CallbackContext) -> int:
    user_code = update.message.text
    if user_code == CORRECT_CODE:
        await update.message.reply_text('Access granted. Here are your links:')
        for link in LINKS:
            await update.message.reply_text(link)
        return ConversationHandler.END
    else:
        await update.message.reply_text('Incorrect code. Please try again or type /cancel to stop.')
        return CODE

# Hàm hủy bỏ quy trình xác thực
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Action canceled.')
    return ConversationHandler.END

def main():
    # Thay 'YOUR_TOKEN' bằng token của bạn
    application = Application.builder().token("6828748542:AAEwhxdMfmapbx8aSHBrhm-GI9MBANH9bqU").build()

    # Thêm handler cho lệnh /start
    application.add_handler(CommandHandler("start", start))

    # Thêm handler cho lệnh /help
    application.add_handler(CommandHandler("help", help_command))

    # Thêm handler cho lệnh /group
    application.add_handler(CommandHandler("group", group_command))

    # Thêm handler cho lệnh /about
    application.add_handler(CommandHandler("about", about_command))

    # Thêm handler cho lệnh /access_database sử dụng ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('access_database', access_database)],
        states={
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Bắt đầu bot
    application.run_polling()

if __name__ == '__main__':
    main()
