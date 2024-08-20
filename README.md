# Dify_Pipeline_OpenwebUI
通过该项目将Dify通过Pipeline接入OpenwebUI，可以兼并OpenwebUI的前端优势和相应生态以及Dify强大的模型可拓展性和Workflow的效益。

08.15 初步测试没有遇到问题

08.19 很遗憾，当前前端似乎没有办法正确的在pipe中传入chat_id，而Dify的conversation_id是自动生成的。我们没法很好的建立两者的映射关系，因为Chat_id并不存在于Pipe方法传入的参数内，并且 chat_id 并不由“新建会话”生成，而是会话界面发送了任意一条信息后生成的。这会导致不同会话的上下文没有办法保持独立。

08.20 参照OUI的某个issue进行重构，对Pipeline类做了以下改动：

1. 在`__init__`方法中，我们添加了`self.chat_id = None`来初始化chat_id

2. 添加了`inlet`方法，用于存储从body中获取的chat_id

3. 在`pipe`方法中，我们现在使用`self.chat_id`而不是从body中获取chat_id

4. 在处理conversation_id时，我们同样使用`self.chat_id`

5. 在`_handle_streaming_response`和`_handle_blocking_response`方法中，我们也使用`self.chat_id`来存储和检索conversation_id

这样的话，现在chat_id是在类的实例变量中存储的，而不是每次都从body中获取。测试下来好像没有问题，但是这种方法在并发访问时一定会有问题。后面再改吧

8.21 

