import { NotFoundPage } from "@/components/ui/404-page-not-found";

export default function NotFound() {
  return (
    <>
      <title>404 - Page Not Found | Asklytics</title>
      <meta
        name="description"
        content="The page you are looking for is not available or has been moved."
      />
      <NotFoundPage />
    </>
  );
}
