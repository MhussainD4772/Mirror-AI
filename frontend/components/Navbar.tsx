import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "../contexts/AuthContext";

const Navbar: React.FC = () => {
  const router = useRouter();
  const { user, loading, signOut } = useAuth();

  const isActive = (path: string) => {
    return router.pathname === path;
  };

  const handleLogout = async () => {
    await signOut();
  };

  return (
    <nav className="bg-slate-900 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <span className="text-xl font-semibold text-slate-100">
                Mirror AI
              </span>
            </Link>
          </div>

          {!loading && (
            <div className="flex items-center space-x-8">
              {user ? (
                <>
                  <Link
                    href="/"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive("/")
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:text-slate-100 hover:bg-slate-800"
                    }`}
                  >
                    Reflect
                  </Link>
                  <Link
                    href="/dashboard"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive("/dashboard")
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:text-slate-100 hover:bg-slate-800"
                    }`}
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-2 rounded-md text-sm font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive("/login")
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:text-slate-100 hover:bg-slate-800"
                    }`}
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/signup"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive("/signup")
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:text-slate-100 hover:bg-slate-800"
                    }`}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
