/**
 * Resource Detail Page
 */
import { useParams, useNavigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import {
  Box,
  Heading,
  Text,
  Spinner,
  Center,
  VStack,
  HStack,
  Button,
  Badge,
  Divider,
  useToast,
} from "@chakra-ui/react";
import { useAuth } from "@/hooks/useAuth";
import { useResource, useDeleteResource } from "@/hooks/useResources";

export default function ResourceDetailPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const { user } = useAuth();
  const { id } = useParams<{ id: string }>();
  const { data: resource, isLoading, isError } = useResource(id || "");
  const deleteResourceMutation = useDeleteResource();

  const isOwner = user && resource && user.id === resource.user_id;

  const handleEdit = () => {
    navigate(`/resources/${id}/edit`);
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this resource? This action cannot be undone.")) {
      return;
    }

    try {
      await deleteResourceMutation.mutateAsync(id || "");
      toast({
        title: "Resource deleted",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      navigate("/resources");
    } catch {
      toast({
        title: "Failed to delete resource",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <Center py={12}>
          <Spinner />
        </Center>
      </Layout>
    );
  }

  if (isError || !resource) {
    return (
      <Layout>
        <Box textAlign="center" py={12}>
          <Text>Resource not found</Text>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <VStack align="stretch" spacing={6}>
        {/* Header with title and actions */}
        <HStack justify="space-between" align="flex-start">
          <VStack align="flex-start" spacing={2}>
            <Heading size="lg">{resource.title}</Heading>
            <HStack spacing={2}>
              <Badge colorScheme="blue">{resource.type}</Badge>
              {resource.status && (
                <Badge
                  colorScheme={
                    resource.status === "SOLVED"
                      ? "green"
                      : resource.status === "ARCHIVED"
                      ? "gray"
                      : "yellow"
                  }
                >
                  {resource.status}
                </Badge>
              )}
              {resource.is_verified && (
                <Badge colorScheme="green">Verified</Badge>
              )}
            </HStack>
          </VStack>

          {isOwner && (
            <HStack spacing={2}>
              <Button
                size="sm"
                colorScheme="blue"
                onClick={handleEdit}
              >
                Edit
              </Button>
              <Button
                size="sm"
                colorScheme="red"
                onClick={handleDelete}
                isLoading={deleteResourceMutation.isPending}
              >
                Delete
              </Button>
            </HStack>
          )}
        </HStack>

        {/* Content */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm">
          <Text whiteSpace="pre-wrap" mb={4}>
            {resource.content_text}
          </Text>

          {resource.system_tags.length > 0 && (
            <>
              <Divider my={4} />
              <VStack align="flex-start" spacing={2}>
                <Text fontSize="sm" fontWeight="bold" color="gray.600">
                  Topics
                </Text>
                <HStack spacing={2} flexWrap="wrap">
                  {resource.system_tags.map((tag) => (
                    <Badge key={tag} colorScheme="blue" variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </HStack>
              </VStack>
            </>
          )}

          <Divider my={4} />
          <Text fontSize="xs" color="gray.500">
            Created {new Date(resource.created_at).toLocaleDateString()}{" "}
            {new Date(resource.created_at).toLocaleTimeString()}
          </Text>
        </Box>
      </VStack>
    </Layout>
  );
}
