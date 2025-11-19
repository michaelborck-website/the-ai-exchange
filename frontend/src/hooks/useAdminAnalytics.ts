import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

interface TopResource {
  resource_id: string;
  view_count: number;
  save_count: number;
  tried_count: number;
  title?: string;
}

interface PlatformAnalytics {
  platform_stats: {
    total_resources: number;
    total_views: number;
    total_saves: number;
    total_tried: number;
    total_forks: number;
    total_comments: number;
    avg_views_per_resource: number;
    avg_saves_per_resource: number;
  };
  top_resources: TopResource[];
}

interface DisciplineStats {
  count: number;
  total_views: number;
  total_saves: number;
}

interface AnalyticsByDiscipline {
  by_discipline: Record<string, DisciplineStats>;
}

/**
 * Fetch platform-wide analytics for admin dashboard
 */
export const usePlatformAnalytics = () => {
  return useQuery({
    queryKey: ["adminPlatformAnalytics"],
    queryFn: async () => {
      const response = await apiClient.get<PlatformAnalytics>(
        "/admin/analytics"
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Fetch analytics breakdown by discipline
 */
export const useAnalyticsByDiscipline = () => {
  return useQuery({
    queryKey: ["adminAnalyticsByDiscipline"],
    queryFn: async () => {
      const response = await apiClient.get<AnalyticsByDiscipline>(
        "/admin/analytics/by-discipline"
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
