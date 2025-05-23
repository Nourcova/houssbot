from telegram import Update, Message
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store question and reply mappings
question_map = {}  # key: forwarded_message_id, value: original_user_id

TEACHERS_GROUP_ID = -1002537355659  # Replace with your teacher group chat ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me your question and I’ll get an answer from a teacher.")


async def handle_student_question(update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message
    user_id = user_message.from_user.id

    # Forward question to teacher group
    forwarded_message = await context.bot.forward_message(
        chat_id=TEACHERS_GROUP_ID,
        from_chat_id=user_id,
        message_id=user_message.message_id)

    # Save mapping
    question_map[forwarded_message.message_id] = user_id

    await user_message.reply_text(
        "Your question has been sent to a teacher. Please wait for a response."
    )


async def handle_teacher_reply(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    reply = update.message
    if reply.reply_to_message and reply.chat_id == TEACHERS_GROUP_ID:
        original_message_id = reply.reply_to_message.message_id
        if original_message_id in question_map:
            student_id = question_map[original_message_id]
            await context.bot.send_message(
                chat_id=student_id, text=f"Teacher's answer:\n{reply.text}")
        else:
            logger.info("No mapping found for replied message.")


def main():
    app = ApplicationBuilder().token(
        "7779445610:AAGKpTrVjgmQTrOkhuhu7q3CwVa3BwsaGFM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE,
                       handle_student_question))
    app.add_handler(
        MessageHandler(filters.REPLY & filters.Chat(TEACHERS_GROUP_ID),
                       handle_teacher_reply))

    app.run_polling()


if __name__ == '__main__':
    main()
