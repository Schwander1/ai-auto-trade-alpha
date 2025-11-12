import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'alpine_verified_trades_2006_2025.csv')
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return new NextResponse('Backtest data file not found. Please contact support.', { 
        status: 404,
        headers: {
          'Content-Type': 'text/plain',
        },
      })
    }

    const fileBuffer = fs.readFileSync(filePath)

    return new NextResponse(fileBuffer, {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="Alpine_Backtest_2006_2025.csv"',
        'Cache-Control': 'public, max-age=3600',
      },
    })
  } catch (error) {
    console.error('Error serving CSV:', error)
    return new NextResponse('Error serving file. Please try again later.', { 
      status: 500,
      headers: {
        'Content-Type': 'text/plain',
      },
    })
  }
}
