import subprocess
import os
import logging
import asyncio
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import datetime
import server

# Token and channel ID (use environment variables in production)
TOKEN_INSECURE = "7287179780:AAEJAn7-WmWGlj94s-yUl_XV55aUXOH5KmA"
CHANNEL_ID = '@Daily_Combo_Secret_Code'

# Environment variable retrieval
if os.name == 'posix':
    TOKEN = subprocess.run(["printenv", "HAMSTER_BOT_TOKEN"], text=True, capture_output=True).stdout.strip()
elif os.name == 'nt':
    TOKEN = subprocess.run(["echo", "%HAMSTER_BOT_TOKEN%"], text=True, capture_output=True, shell=True).stdout.strip()
    TOKEN = "" if TOKEN == "%HAMSTER_BOT_TOKEN%" else TOKEN

AUTHORIZED_USERS = []
EXCLUSIVE = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member_status = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member_status.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            return True
        return False
    except telegram.error.BadRequest as e:
        server.logger.warning(f"Error checking membership: {str(e)}")
        await context.bot.send_message(
            chat_id=user_id,
            text="Could not verify membership."
        )
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    is_member = await check_membership(user_id, context)

    if is_member:
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(user_id)
        await context.bot.send_message(chat_id=user_id, text="Welcome! You are authorized to use the bot.")
    else:
        await context.bot.send_message(chat_id=user_id, text="Please subscribe to our channel to use this bot. @Daily_Combo_Secret_Code")
        return
    await context.bot.send_message(chat_id=user_id, text="🐹")
    await context.bot.send_message(
        chat_id=user_id,
        text="The Commands are:\n*/cube*\n*/train*\n*/merge*\n*/twerk*\n*/poly*\n*/trim*\n*/cafe*\n*/zoo*\n*/gang*\n*/all*\nThese will generate 4 keys for their respective games\.",
        parse_mode='MARKDOWNV2'
    )
    await context.bot.send_message(
        chat_id=user_id,
        text="You can also set how many keys are generated\. For example, */cube 8* will generate *EIGHT* keys for the cube game\.",
        parse_mode='MARKDOWNV2'
    )

async def game_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chosen_game: int,
    all: bool,
    delay=0
):
    user_id = update.effective_chat.id
    is_member = await check_membership(user_id, context)

    if is_member:
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(user_id)
        await context.bot.send_message(chat_id=user_id, text="Welcome! You are authorized to use the bot.")
    else:
        await context.bot.send_message(chat_id=user_id, text="Please subscribe to our channel to use this bot. @Daily_Combo_Secret_Code")
        return
    
    if EXCLUSIVE and not update.effective_chat.id in AUTHORIZED_USERS:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="create your own bot\.",
            parse_mode='MARKDOWNV2'
        )
        with open(f'{os.path.dirname(__file__)}/unauthorized', 'a') as file:
            unauthorized_message = f"Unauthorized User: {update.effective_chat.first_name} - {update.effective_chat.username}: {user_id}"
            server.logger.warning(unauthorized_message)
            file.write(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} {unauthorized_message}\n")
        return

    # Delay for the /all command
    await asyncio.sleep(delay)
    server.logger.info(f"Delay for {delay} seconds")

    server.logger.info(f"Generating for client: {update.effective_chat.first_name} - {update.effective_chat.username}: {user_id}")
    if not all:
        await context.bot.send_message(chat_id=user_id, text="🐹")
        await context.bot.send_message(chat_id=user_id, text=f"Generating\.\.\.", parse_mode='MARKDOWNV2')
        await context.bot.send_message(chat_id=user_id, text=f"This will only take a moment\.\.\.", parse_mode='MARKDOWNV2')

    no_of_keys = int(context.args[0]) if context.args else 4
    keys = await server.run(chosen_game=chosen_game, no_of_keys=no_of_keys)
    if not keys:
        await context.bot.send_message(chat_id=user_id, text="No keys were generated. Please try again later.")
        return
    
    formatted_keys = "\n".join(keys)
    
    if not formatted_keys.strip():
        await context.bot.send_message(chat_id=user_id, text="No valid keys to display.")
        return
    
    try:
        await context.bot.send_message(chat_id=user_id, text=f"{formatted_keys}", parse_mode='MARKDOWNV2')
    except telegram.error.BadRequest as e:
        logging.error(f"Failed to send message: {str(e)}")
    generated_keys = [f"`{key}`" for key in keys]
    formatted_keys = '\n'.join(generated_keys)
    await context.bot.send_message(chat_id=user_id, text=f"{formatted_keys}", parse_mode='MARKDOWNV2')
    server.logger.info("Message sent to the client.")

# Define handlers for different commands
async def cube(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=1, all=all)

async def train(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=2, all=all)

async def merge(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=3, all=all)

async def twerk(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=4, all=all)

async def poly(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=5, all=all)

async def trim(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=6, all=all)

async def cafe(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=7, all=all)

async def zoo(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=8, all=all)

async def gang(update: Update, context: ContextTypes.DEFAULT_TYPE, all=False):
    await game_handler(update, context, chosen_game=9, all=all)

async def all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if EXCLUSIVE and not update.effective_chat.id in AUTHORIZED_USERS:
        return
    
    server.logger.info(f"Generating ALL GAMES for client: {update.effective_chat.first_name} - {update.effective_chat.username}: {update.effective_chat.id}")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="🐹")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Currently generating for all games\.\.\.", parse_mode='MARKDOWNV2')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Come Back in about 5\-10 minutes\.", parse_mode='MARKDOWNV2')

    # Wait a certain number of seconds between each game
    tasks = [game_handler(update, context, i + 1, True, i * 30) for i in range(10)]
    await asyncio.gather(*tasks)

# Entry point for Google Cloud Functions
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN or TOKEN_INSECURE).build()
    server.logger.info("Server is running. Awaiting users...")

    application.add_handler(CommandHandler('start', start, block=False))
    application.add_handler(CommandHandler('cube', cube, block=False))
    application.add_handler(CommandHandler('train', train, block=False))
    application.add_handler(CommandHandler('merge', merge, block=False))
    application.add_handler(CommandHandler('twerk', twerk, block=False))
    application.add_handler(CommandHandler('poly', poly, block=False))
    application.add_handler(CommandHandler('trim', trim, block=False))
    application.add_handler(CommandHandler('zoo', zoo, block=False))

    application.add_handler(CommandHandler('all', all, block=False))


    application.run_polling()
