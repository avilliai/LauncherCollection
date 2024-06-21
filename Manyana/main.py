from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage
if __name__ == '__main__':
    bot = Mirai(919467430, adapter=WebSocketAdapter(
        verify_key=1234567890, host='localhost', port=23456
    ))
    @bot.on(GroupMessage)
    async def fafaf(event: GroupMessage):
        if str(event.message_chain)=="1":
            await bot.send(event,"helo")
    bot.run()