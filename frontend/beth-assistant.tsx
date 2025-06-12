"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ArrowRight, Plus, Paperclip, Camera, Send } from "lucide-react"

export default function Component() {
  const [inputValue, setInputValue] = useState("")

  const recentChats = Array(9).fill("How can I better update...")

  const suggestionCards = [
    { icon: "✱", text: "I would like to know about design tokens" },
    { icon: "✦", text: "I would like to know about design tokens" },
    { icon: "♥", text: "I would like to know about design tokens" },
    { icon: "✱", text: "I would like to know about design tokens" },
    { icon: "❅", text: "I would like to know about design tokens" },
    { icon: "✱", text: "I would like to know about design tokens" },
  ]

  const navTabs = ["Notion", "Figma", "Github", "Email", "Calendar"]

  return (
    <div className="min-h-screen bg-cover bg-center" style={{ backgroundImage: "url(/assets/gradient.png)" }}>
      {/* Header */}
      <div className="bg-[#171717] text-white px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <img src="/assets/smiley.svg" alt="Smiley" className="w-6 h-6" />
          </div>
          <span className="text-xl font-semibold">BETH'S ASSISTANT</span>
        </div>
        <div className="flex items-center gap-8">
          <span className="text-lg font-medium">FRIDAY</span>
          <span className="text-lg font-medium">JUNE 6, 2025</span>
          <span className="text-lg font-medium">11:25 AM</span>
        </div>
      </div>

      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Sidebar */}
        <div className="max-w-[270px] w-[270px] p-4 flex flex-col">
          {/* Recents Chat Header */}
          <div className="bg-[#171717] text-white px-4 py-3 rounded-lg flex items-center justify-between mb-4">
            <span className="font-medium">Recents Chat</span>
            <ArrowLeft className="w-5 h-5" />
          </div>

          {/* Chat History */}
          <div className="flex-1 space-y-2 mb-4">
            {recentChats.map((chat, index) => (
              <div key={index} className="text-[#404040] py-2 px-2 hover:bg-white/20 rounded cursor-pointer">
                {chat}
              </div>
            ))}
          </div>

          {/* New Chat Button */}
          <Button className="bg-[#171717] text-white hover:bg-[#272727] rounded-lg py-6 text-lg font-medium">
            <span>New Chat</span>
            <Plus className="w-5 h-5 ml-2" />
          </Button>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 flex flex-col">
          {/* Navigation Tabs */}
          <div className="flex gap-4 mb-8 w-full">
            {navTabs.map((tab, index) => (
              <Button
                key={tab}
                className={`flex-1 py-3 rounded-lg font-medium ${
                  index === 1 ? "bg-[#171717] text-white" : "bg-[#171717] text-white hover:bg-[#272727]"
                }`}
              >
                {tab}
              </Button>
            ))}
          </div>

          {/* Greeting */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-serif text-[#171717] mb-2">
              Good Morning Beth! What can I help you with today?
            </h1>
          </div>

          {/* Suggestion Cards */}
          <div className="grid grid-cols-2 gap-4 mb-8 max-w-4xl mx-auto">
            {suggestionCards.map((card, index) => (
              <div
                key={index}
                className="bg-white border-2 border-[#171717] rounded-lg p-4 flex items-center gap-4 hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="bg-[#171717] text-white w-12 h-12 rounded-lg flex items-center justify-center text-xl">
                  <img src="/assets/shapes/svg/shape=5.svg" alt="Shape 5" className="w-6 h-6" />
                </div>
                <span className="flex-1 text-[#171717] font-medium">{card.text}</span>
                <ArrowRight className="w-5 h-5 text-[#171717]" />
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="mt-auto max-w-4xl mx-auto w-full">
            <div className="flex flex-col gap-2">
              {/* Main Input Container */}
              <div className="px-3 py-4 bg-[#F7F7F7] shadow-sm rounded border-2 border-black flex flex-col gap-3">
                {/* Text Input */}
                <div className="flex-1 px-3.5 py-2.5 bg-white shadow-sm rounded border border-black flex items-center gap-2">
                  <input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask me a question..."
                    className="flex-1 text-black text-base font-medium leading-5 bg-transparent border-none outline-none placeholder:text-black"
                    style={{ fontFamily: "Mabry Pro" }}
                  />
                </div>
              </div>

              {/* Bottom Controls */}
              <div className="flex justify-between items-center">
                {/* Left Side - Attachment Buttons */}
                <div className="flex items-center gap-2">
                  <Button className="p-2.5 bg-black rounded flex items-center justify-center hover:bg-gray-800">
                    <Paperclip className="w-6 h-6 text-[#F7F7F7]" />
                  </Button>
                  <Button className="p-2.5 bg-black rounded flex items-center justify-center hover:bg-gray-800">
                    <Camera className="w-6 h-6 text-[#F7F7F7]" />
                  </Button>
                </div>

                {/* Right Side - Counter and Send */}
                <div className="flex items-center gap-4">
                  <span
                    className="text-right text-[#404040] text-base font-normal leading-4"
                    style={{ fontFamily: "Mabry Pro" }}
                  >
                    0/1000
                  </span>
                  <Button className="p-2 bg-[#2180EC] rounded-md flex items-center justify-center hover:bg-blue-600">
                    <Send className="w-6 h-6 text-[#F7F7F7]" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
