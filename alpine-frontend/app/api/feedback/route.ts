import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { email, message } = await request.json()

    // Validate message
    if (!message || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // In production, use SendGrid or similar
    // For now, you can use a simple email service or log to database

    // Option 1: Log to server (you check logs)
    console.log('=== NEW FEEDBACK ===')
    console.log('From:', email || 'Anonymous')
    console.log('Message:', message)
    console.log('Timestamp:', new Date().toISOString())
    console.log('===================')

    // Option 2: Send via SendGrid (recommended)
    /*
    const sgMail = require('@sendgrid/mail');
    sgMail.setApiKey(process.env.SENDGRID_API_KEY);

    await sgMail.send({
      to: 'alpine.signals@proton.me',
      from: 'noreply@alpineanalytics.com', // Verified sender
      replyTo: email || undefined,
      subject: 'New Feedback from Website',
      text: `
From: ${email || 'Anonymous'}
Time: ${new Date().toISOString()}

Message:
${message}
      `,
    });
    */

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Feedback error:', error)
    return NextResponse.json(
      { error: 'Failed to send feedback' },
      { status: 500 }
    )
  }
}

