// Utility component to format AI assistant messages with better typography
import React from 'react'

interface FormattedMessageProps {
    content: string
    role: 'user' | 'assistant'
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({ content, role }) => {
    if (role === 'user') {
        // User messages: simple display
        return <p className="text-[15px] leading-relaxed">{content}</p>
    }

    // AI assistant messages: enhanced formatting
    const formatContent = (text: string) => {
        const lines = text.split('\n')
        const elements: JSX.Element[] = []
        let currentParagraph: string[] = []
        let listItems: string[] = []

        const flushParagraph = () => {
            if (currentParagraph.length > 0) {
                elements.push(
                    <p key={`p-${elements.length}`} className="mb-3 leading-relaxed text-gray-800">
                        {currentParagraph.join(' ')}
                    </p>
                )
                currentParagraph = []
            }
        }

        const flushList = () => {
            if (listItems.length > 0) {
                elements.push(
                    <ul key={`ul-${elements.length}`} className="mb-3 ml-4 space-y-1">
                        {listItems.map((item, i) => (
                            <li key={i} className="text-gray-800 leading-relaxed">
                                <span className="text-purple-600 font-bold mr-2">•</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                )
                listItems = []
            }
        }

        lines.forEach((line) => {
            const trimmed = line.trim()

            // Empty line - flush current paragraph/list
            if (!trimmed) {
                flushParagraph()
                flushList()
                return
            }

            // Heading (starts with **)
            if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                flushParagraph()
                flushList()
                const heading = trimmed.slice(2, -2)
                elements.push(
                    <h3 key={`h-${elements.length}`} className="font-bold text-gray-900 mb-2 mt-3 first:mt-0">
                        {heading}
                    </h3>
                )
                return
            }



            // List item (starts with - or •)
            if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
                flushParagraph()
                const item = trimmed.substring(2).trim()
                listItems.push(formatInlineStyles(item))
                return
            }

            // Slide reference (e.g., [Slide 5])
            if (trimmed.match(/^\[Slide \d+\]/)) {
                flushParagraph()
                flushList()
                elements.push(
                    <div key={`slide-${elements.length}`} className="inline-flex items-center bg-purple-100 text-purple-700 px-3 py-1 rounded-lg text-sm font-medium mb-2">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {trimmed}
                    </div>
                )
                return
            }

            // Regular paragraph text
            flushList()
            currentParagraph.push(formatInlineStyles(trimmed))
        })

        // Flush any remaining content
        flushParagraph()
        flushList()

        return elements
    }

    // Format inline styles (bold, code, etc.)
    const formatInlineStyles = (text: string): string => {
        // Remove ** for bold (we'll handle it with CSS)
        return text.replace(/\*\*([^*]+)\*\*/g, '$1')
    }

    return (
        <div className="text-[15px] space-y-1">
            {formatContent(content)}
        </div>
    )
}
