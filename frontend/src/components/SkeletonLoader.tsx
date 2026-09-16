import React from 'react'

interface SkeletonProps {
  className?: string
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-gray-700 rounded ${className}`} />
  )
}

export const DocumentSkeleton: React.FC = () => {
  return (
    <div className="p-4 border-b border-gray-700">
      <div className="flex items-start justify-between mb-2">
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  )
}

export const ChatSkeleton: React.FC = () => {
  return (
    <div className="p-3 hover:bg-gray-700 cursor-pointer">
      <Skeleton className="h-5 w-3/4 mb-2" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  )
}

export const MessageSkeleton: React.FC = () => {
  return (
    <div className="p-4 mb-4">
      <div className="flex items-start gap-3">
        <Skeleton className="h-8 w-8 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    </div>
  )
}

export const MCPSkeleton: React.FC = () => {
  return (
    <div className="p-4 border-b border-gray-700">
      <div className="flex items-start justify-between mb-2">
        <Skeleton className="h-5 w-1/4" />
        <Skeleton className="h-6 w-6 rounded-full" />
      </div>
      <Skeleton className="h-4 w-1/3 mb-2" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  )
}

export default Skeleton