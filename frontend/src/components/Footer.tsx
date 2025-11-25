/**
 * Footer Component
 * Navigation for legal, support, and general information
 */

import { Box, VStack, HStack, Text, Link, Divider, SimpleGrid } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

export function Footer() {
  const navigate = useNavigate();

  const handleNavClick = (path: string) => {
    navigate(path);
    window.scrollTo(0, 0);
  };

  return (
    <Box bg="gray.900" color="gray.100" py={12} px={4} mt={12}>
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} maxW="6xl" mx="auto" mb={8}>
        {/* About & Quick Links */}
        <VStack align="flex-start" spacing={4}>
          <Text fontSize="sm" fontWeight="bold" color="white" mb={2}>
            The AI Exchange
          </Text>
          <VStack align="flex-start" spacing={2} fontSize="sm">
            <Link onClick={() => handleNavClick("/about")} _hover={{ color: "blue.300" }}>
              About Us
            </Link>
            <Link onClick={() => handleNavClick("/getting-started")} _hover={{ color: "blue.300" }}>
              Getting Started
            </Link>
            <Link onClick={() => handleNavClick("/resources")} _hover={{ color: "blue.300" }}>
              Browse Ideas
            </Link>
          </VStack>
        </VStack>

        {/* Legal & Compliance */}
        <VStack align="flex-start" spacing={4}>
          <Text fontSize="sm" fontWeight="bold" color="white" mb={2}>
            Legal & Policies
          </Text>
          <VStack align="flex-start" spacing={2} fontSize="sm">
            <Link onClick={() => handleNavClick("/legal")} _hover={{ color: "blue.300" }}>
              Privacy & Terms
            </Link>
            <Link onClick={() => handleNavClick("/support")} _hover={{ color: "blue.300" }}>
              Code of Conduct
            </Link>
            <Link onClick={() => handleNavClick("/legal")} _hover={{ color: "blue.300" }}>
              Accessibility
            </Link>
          </VStack>
        </VStack>

        {/* Support */}
        <VStack align="flex-start" spacing={4}>
          <Text fontSize="sm" fontWeight="bold" color="white" mb={2}>
            Support & Feedback
          </Text>
          <VStack align="flex-start" spacing={2} fontSize="sm">
            <Link onClick={() => handleNavClick("/support")} _hover={{ color: "blue.300" }}>
              Help Center
            </Link>
            <Link onClick={() => handleNavClick("/support")} _hover={{ color: "blue.300" }}>
              Contact Us
            </Link>
            <Link
              href="mailto:michael.borck@curtin.edu.au"
              _hover={{ color: "blue.300" }}
            >
              Email Support
            </Link>
          </VStack>
        </VStack>
      </SimpleGrid>

      <Divider borderColor="gray.700" my={6} />

      {/* Bottom Section */}
      <VStack spacing={4} maxW="6xl" mx="auto" align="stretch" fontSize="xs" color="gray.400">
        <HStack justify="space-between" flexWrap="wrap">
          <Text>
            &copy; {new Date().getFullYear()} Curtin University. The AI Exchange is an internal platform for the Curtin community.
          </Text>
        </HStack>
        <HStack spacing={6} flexWrap="wrap" fontSize="xs">
          <Link onClick={() => handleNavClick("/legal")} _hover={{ color: "gray.200" }}>
            Privacy Policy
          </Link>
          <Link onClick={() => handleNavClick("/legal")} _hover={{ color: "gray.200" }}>
            Terms of Use
          </Link>
          <Link onClick={() => handleNavClick("/about")} _hover={{ color: "gray.200" }}>
            Licensing
          </Link>
          <Link onClick={() => handleNavClick("/support")} _hover={{ color: "gray.200" }}>
            Report Content
          </Link>
        </HStack>
        <Text fontSize="xs" color="gray.500">
          Built with React, FastAPI, and open source software • Powered by human oversight and AI assistance
        </Text>
      </VStack>
    </Box>
  );
}
