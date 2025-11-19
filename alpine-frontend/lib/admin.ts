import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

/**
 * Check if current user is admin
 */
export function useIsAdmin(): boolean {
  const { data: session } = useSession()
  return (session?.user as any)?.isAdmin === true
}

/**
 * Hook to protect admin-only pages
 * Redirects to login if not authenticated
 * Redirects to dashboard if not admin
 */
export function useRequireAdmin() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const isAdmin = useIsAdmin()

  useEffect(() => {
    if (status === "loading") return

    if (status === "unauthenticated") {
      router.push("/login?redirect=/execution")
      return
    }

    if (status === "authenticated" && !isAdmin) {
      router.push("/dashboard?error=admin_required")
      return
    }
  }, [status, isAdmin, router])

  return {
    isAdmin,
    isLoading: status === "loading",
    isAuthenticated: status === "authenticated"
  }
}

/**
 * Server-side admin check utility
 */
export async function checkAdminAccess(session: any): Promise<boolean> {
  if (!session) return false
  return (session.user as any)?.isAdmin === true
}
