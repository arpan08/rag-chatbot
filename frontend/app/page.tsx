"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

type Message = {
  role: "user" | "bot";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      content: "Hi Arpan, ask me anything from your RAG knowledge base.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: userMessage.content,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();

      const botMessage: Message = {
        role: "bot",
        content: data.answer ?? "No answer returned from backend.",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "Something went wrong while calling the backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 p-4">
      <div className="mx-auto flex min-h-[90vh] max-w-3xl items-center">
        <Card className="flex h-[85vh] w-full flex-col">
          <CardHeader>
            <CardTitle>RAG Chatbot</CardTitle>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col gap-4 overflow-hidden">
            <ScrollArea className="flex-1 rounded-md border bg-slate-50 p-4">
              <div className="flex flex-col gap-3">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                      message.role === "user"
                        ? "ml-auto bg-black text-white"
                        : "mr-auto border bg-white text-black"
                    }`}
                  >
                    {message.content}
                  </div>
                ))}

                {loading && (
                  <div className="mr-auto max-w-[80%] rounded-lg border bg-white px-4 py-2 text-sm">
                    Thinking...
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about CPT, PDF data, or anything..."
                className="min-h-[60px]"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />

              <Button onClick={sendMessage} disabled={loading}>
                Send
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}