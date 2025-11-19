import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Check if user is admin
    const isAdmin = (session.user as any)?.isAdmin === true;
    if (!isAdmin) {
      return NextResponse.json(
        { error: "Admin access required" },
        { status: 403 }
      );
    }

    // Fetch data from Argo backend
    const argoUrl = process.env.NEXT_PUBLIC_ARGO_API_URL || process.env.ARGO_API_URL || 'http://178.156.194.174:8000';
    const adminKey = process.env.ADMIN_API_KEY || '';

    const argoResponse = await fetch(
      `${argoUrl}/api/v1/execution/account-states`,
      {
        headers: {
          "X-Admin-API-Key": adminKey,
        },
      }
    );

    if (!argoResponse.ok) {
      throw new Error(`Argo API returned ${argoResponse.status}`);
    }

    const data = await argoResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching account states:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
