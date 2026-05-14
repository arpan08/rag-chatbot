"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

type Message = {
  role: "user" | "assistant";
  content: string;
  thinkingTimeSec?: number;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi Arpan, ask me anything from your RAG knowledge base.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [liveThinkingTime, setLiveThinkingTime] = useState(0);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;

    if (loading) {
      setLiveThinkingTime(0);

      interval = setInterval(() => {
        setLiveThinkingTime((prev) => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [loading]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, liveThinkingTime]);

  async function sendMessage() {
    if (!input.trim()) return;

    const question = input;

    const userMessage: Message = {
      role: "user",
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        thinkingTimeSec: data.thinkingTimeSec,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Backend is not reachable or returned an error. Please check Python backend and Java tool service.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 p-4">
      <div className="mx-auto flex min-h-[90vh] max-w-3xl items-center">
        <Card className="flex h-[85vh] w-full flex-col overflow-hidden">
          <CardHeader>
            <CardTitle>RAG Chatbot</CardTitle>
          </CardHeader>

          <CardContent className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden">
            <ScrollArea className="min-h-0 flex-1 rounded-md border bg-slate-50">
              <div className="flex max-h-full flex-col gap-3 overflow-y-auto overflow-x-hidden p-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`max-w-[80%] whitespace-pre-wrap break-words rounded-lg px-4 py-2 text-sm ${
                      message.role === "user"
                        ? "ml-auto bg-black text-white"
                        : "mr-auto border bg-white text-black"
                    }`}
                  >
                    <div>{message.content}</div>

                    {message.role === "assistant" &&
                      message.thinkingTimeSec !== undefined && (
                        <div className="mt-2 text-xs text-slate-500">
                          Answer generated in {message.thinkingTimeSec}s
                        </div>
                      )}
                  </div>
                ))}

                {loading && (
                  <div className="mr-auto max-w-[80%] rounded-lg border bg-white px-4 py-2 text-sm text-black">
                    <div className="flex items-center gap-2">
                      <span>Thinking</span>
                      <span className="animate-pulse">...</span>
                      <span className="text-xs text-slate-500">
                        {liveThinkingTime}s
                      </span>
                    </div>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>
            </ScrollArea>

            <div className="flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about CPT, PDF data, time, weather, or anything..."
                className="max-h-32 min-h-[60px] resize-none overflow-y-auto"
                disabled={loading}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />

              <Button onClick={sendMessage} disabled={loading || !input.trim()}>
                {loading ? "Sending..." : "Send"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}