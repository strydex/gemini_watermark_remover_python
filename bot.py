"""
Telegram Bot - Gemini Watermark Remover
"""
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from gemini_remover import remove_watermark
import tempfile

# Telegram Bot Token
BOT_TOKEN = 'PASTE YOUR TELEGRAM BOT TOKEN HERE'

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    await message.answer(
        "🖼️ <b>Gemini Watermark Remover</b>\n\n"
        "Отправь мне изображение с водяным знаком Gemini, и я удалю его!\n\n"
        "Powered by Reverse Alpha Blending algorithm 🐍",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command"""
    await message.answer(
        "📖 <b>Как использовать:</b>\n\n"
        "1. Отправь мне фото с водяным знаком Gemini\n"
        "2. Я обработаю изображение\n"
        "3. Отправлю очищенную версию\n\n"
        "Поддерживаемые форматы: PNG, JPG, JPEG",
        parse_mode="HTML"
    )

@dp.message()
async def handle_photo(message: types.Message):
    """Handle incoming photos"""
    try:
        # Check if message contains photo
        if not message.photo:
            await message.answer("Пожалуйста, отправь изображение 📷")
            return
        
        # Send "processing" message
        processing_msg = await message.answer("🔄 Обрабатываю изображение...")
        
        # Get the largest photo
        photo = message.photo[-1]
        
        # Download photo
        file = await bot.get_file(photo.file_id)
        file_path = file.file_path
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, "input.jpg")
        output_path = os.path.join(temp_dir, "output.jpg")
        
        # Download file
        await bot.download_file(file_path, input_path)
        
        # Process image
        try:
            result_path = remove_watermark(input_path, output_path)
            
            # Send back the cleaned image
            await message.answer_photo(
                FSInputFile(result_path),
                caption="✅ Watermark removed! 🐍"
            )
            await processing_msg.delete()
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ Ошибка при обработке: {str(e)}")
        
        # Cleanup temp files
        try:
            os.remove(input_path)
            os.remove(result_path)
            os.rmdir(temp_dir)
        except:
            pass
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error: {e}")

async def main():
    """Start the bot"""
    # Delete webhook
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
