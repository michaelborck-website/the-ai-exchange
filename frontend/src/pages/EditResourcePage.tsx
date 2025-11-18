/**
 * Edit Resource Page
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Layout } from "@/components/Layout";
import {
  VStack,
  Heading,
  Input,
  Textarea,
  Button,
  Box,
  useToast,
  FormControl,
  FormLabel,
  Spinner,
  Center,
  Text,
} from "@chakra-ui/react";
import { useAuth } from "@/hooks/useAuth";
import { useResource, useUpdateResource } from "@/hooks/useResources";

export default function EditResourcePage() {
  const navigate = useNavigate();
  const toast = useToast();
  const { user } = useAuth();
  const { id } = useParams<{ id: string }>();
  const { data: resource, isLoading, isError } = useResource(id || "");
  const updateMutation = useUpdateResource();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  // Initialize form with resource data
  useEffect(() => {
    if (resource) {
      setTitle(resource.title);
      setContent(resource.content_text);
    }
  }, [resource]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      toast({
        title: "Please fill in all fields",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      await updateMutation.mutateAsync({
        id: id || "",
        data: {
          title,
          content_text: content,
        },
      });

      toast({
        title: "Resource updated",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      navigate(`/resources/${id}`);
    } catch {
      toast({
        title: "Failed to update resource",
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

  // Check ownership
  if (user?.id !== resource.user_id) {
    return (
      <Layout>
        <Box textAlign="center" py={12}>
          <Text color="red.600">You don't have permission to edit this resource</Text>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box maxW="2xl">
        <Heading size="lg" mb={6}>
          Edit Resource
        </Heading>

        <Box as="form" onSubmit={handleSubmit} bg="white" p={6} borderRadius="lg" boxShadow="sm">
          <VStack spacing={6}>
            <FormControl>
              <FormLabel>Title</FormLabel>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter title"
                required
              />
            </FormControl>

            <FormControl>
              <FormLabel>Content</FormLabel>
              <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter content"
                minHeight="300px"
                required
              />
            </FormControl>

            <div style={{ display: "flex", gap: "12px", width: "100%" }}>
              <Button
                colorScheme="blue"
                type="submit"
                isLoading={updateMutation.isPending}
                flex={1}
              >
                Save Changes
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate(`/resources/${id}`)}
                flex={1}
              >
                Cancel
              </Button>
            </div>
          </VStack>
        </Box>
      </Box>
    </Layout>
  );
}
