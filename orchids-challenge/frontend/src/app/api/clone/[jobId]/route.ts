import { NextRequest, NextResponse } from 'next/server';

// Define the backend URL - this should come from environment variables in production
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string } }
) {
  const jobId = params.jobId;

  try {
    // Forward the request to the backend API
    const response = await fetch(`${BACKEND_URL}/clone/${jobId}/html`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // If the backend returns an error, pass it along
    if (!response.ok) {
      return NextResponse.json(
        { error: `Backend server error: ${response.statusText}` },
        { status: response.status }
      );
    }

    // Get the data from the backend
    const data = await response.json();
    
    // Return the HTML content
    return NextResponse.json({ html: data.html });
  } catch (error) {
    console.error('Error fetching from backend:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend server' },
      { status: 500 }
    );
  }
}
