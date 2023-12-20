import tkinter as tk
from collections import deque
import time

class WeightedGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, node, neighbor, weight):
        if node not in self.graph:
            self.graph[node] = {}
        if neighbor not in self.graph:
            self.graph[neighbor] = {}

        self.graph[node][neighbor] = weight
        self.graph[neighbor][node] = weight

graph = WeightedGraph()
graph.add_edge('A', 'B', 4)
graph.add_edge('A', 'D', 3)
graph.add_edge('A', 'F', 3)
graph.add_edge('B', 'F', 5)
graph.add_edge('B', 'C', 4)
graph.add_edge('C', 'E', 4)
graph.add_edge('D', 'G', 5)

class PathSearchingApp:
    def __init__(self, master):
        self.master = master
        self.target_found = False
        master.title("Path Searching Visualization")

        self.canvas = tk.Canvas(master, width=500, height=300)
        self.canvas.pack()

        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

        self.start_node_label = tk.Label(master, text="Start Node:")
        self.start_node_label.pack(side=tk.LEFT)

        self.start_node_entry = tk.Entry(master)
        self.start_node_entry.pack(side=tk.LEFT)

        self.search_node_label = tk.Label(master, text="Goal Node:")
        self.search_node_label.pack(side=tk.LEFT)

        self.search_node_entry = tk.Entry(master)
        self.search_node_entry.pack(side=tk.LEFT)

        self.bfs_button = tk.Button(master, text="BFS", command=self.bfs_button_clicked)
        self.bfs_button.pack(side=tk.LEFT)

        self.dfs_button = tk.Button(master, text="DFS", command=self.dfs_button_clicked)
        self.dfs_button.pack(side=tk.LEFT)

        self.hill_climbing_button = tk.Button(master, text="Hill Climbing", command=self.hill_climbing_button_clicked)
        self.hill_climbing_button.pack(side=tk.LEFT)
        
        self.beam_search_button = tk.Button(master, text="Beam Search", command=self.beam_search_button_clicked)
        self.beam_search_button.pack(side=tk.LEFT)


        self.vertices = {'A': (200, 250), 'B': (200, 150), 'C': (200, 50),
                         'D': (300, 250), 'E': (400, 50), 'F': (100, 250),
                         'G': (400, 150)}

        self.speed_var = tk.DoubleVar()  # Variable to store simulation speed
        self.speed_scale = tk.Scale(master, from_=0.1, to=2.0, orient=tk.HORIZONTAL, resolution=0.1,
                                    label="Simulation Speed", variable=self.speed_var)
        self.speed_scale.set(1.0)  # Default speed
        self.speed_scale.pack(side=tk.LEFT)

        self.pause_var = tk.BooleanVar()  # Variable to store pause/play state
        self.pause_button = tk.Button(master, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT)

        # Draw vertices and edges
        for node, pos in self.vertices.items():
            self.draw_node(node, pos)
            for neighbor, weight in graph.graph[node].items():
                self.draw_edge(node, neighbor, weight)

        # Count parameters
        self.enqueue_count = 0
        self.queue_size = 0

        # State variables
        self.bfs_running = False
        self.dfs_running = False
        self.hill_climbing_running = False
        self.beam_search_running = False
        
        self.path_label = tk.Label(master, text="")
        self.path_label.pack()

    def draw_node(self, node, pos):
        x, y = pos
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='white')
        self.canvas.create_text(x, y, text=node, font=("Helvetica", 14, 'bold'), fill="black")

    def draw_edge(self, node1, node2, weight):
        x1, y1 = self.vertices[node1]
        x2, y2 = self.vertices[node2]

        # Draw the line
        line = self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

        # Calculate the midpoint for placing the text
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Display the weight on the line
        self.canvas.create_text(mid_x, mid_y, text=str(weight), font=('Arial', 10, 'bold'))

    def update_node_color(self, node, color):
        x, y = self.vertices[node]
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color)
        self.canvas.create_text(x, y, text=node, font=('Arial', 14, 'bold'))

    def toggle_pause(self):
        # Toggle pause/play state
        self.pause_var.set(not self.pause_var.get())
        if self.pause_var.get():
            self.pause_button.config(text="Play")
        else:
            self.pause_button.config(text="Pause")
            if self.bfs_running:
                self.master.after(1, self.bfs_traversal)  # Resume BFS traversal
            elif self.dfs_running:
                self.master.after(1, self.dfs_traversal)  # Resume DFS traversal
            elif self.hill_climbing_running:
                self.master.after(1, self.hill_climbing)  # Resume Hill Climbing

    def reset_colors(self):
        for node in self.vertices:
            self.update_node_color(node, 'white')

    def reset_queue_size(self):
        self.enqueue_count = 0
        self.queue_size = 0

    def bfs_button_clicked(self):
        if not self.bfs_running:
            self.bfs_running = True
            self.bfs_traversal()

    def dfs_button_clicked(self):
        if not self.dfs_running:
            self.dfs_running = True
            self.dfs_traversal()

    def hill_climbing_button_clicked(self):
        if not self.hill_climbing_running:
            self.hill_climbing_running = True
            self.hill_climbing()
    
    def beam_search_button_clicked(self):
        if not self.beam_search_running:
            self.beam_search_running = True
            self.beam_search()

    def bfs_traversal(self):
        self.reset_colors()
        self.reset_queue_size()
        start_node = self.start_node_entry.get()
        search_node = self.search_node_entry.get()
        visited = set()
        queue = deque([(start_node, 0, [])])  # Queue now contains both node, path cost, and the path
        visited.add(start_node)

        while queue and not self.pause_var.get():
            node, path_cost, path = queue.popleft()
            path = path + [node]  # Extend the current path
            self.update_node_color(node, 'green')  # Mark as visited
            self.status_label.config(text=f"Visiting node {node}, Path: {path}, Path Cost: {path_cost}")
            self.master.update()
            time.sleep(1 / self.speed_var.get())  # Adjust speed
            self.enqueue_count += 1
            self.queue_size = len(queue)

            if node == search_node:
                self.status_label.config(
                    text=f"Node {search_node} found! Path: {path}, Path Cost: {path_cost}, Enqueues: {self.enqueue_count}, Queue Size: {self.queue_size}")
                self.bfs_running = False
                return  # Stop the traversal if the node is found

            for neighbor, weight in graph.graph[node].items():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path_cost + weight, path))

        self.status_label.config(
            text=f"All nodes visited. Enqueues: {self.enqueue_count}, Queue Size: {self.queue_size}")
        self.bfs_running = False

    def dfs_util(self, node, search_node, visited, path_cost, path):
        if self.target_found:  # Check if the target node is already found
            return

        visited.add(node)
        path = path + [node]  # Extend the current path
        self.update_node_color(node, 'green')  # if visited, mark green
        self.status_label.config(text=f"Visiting node {node}, Path: {path}, Path Cost: {path_cost}")
        self.master.update()
        time.sleep(1 / self.speed_var.get())  # Pause for visualization

        if node == search_node:
            self.status_label.config(
                text=f"Node {search_node} found! Path: {path}, Path Cost: {path_cost}, Enqueues: {self.enqueue_count}, Queue Size: {self.queue_size}")
            self.target_found = True  # to stop further traversal, set flag to true
            return  # Stop the traversal if the node is found

        for neighbor, weight in graph.graph[node].items():
            if neighbor not in visited and not self.pause_var.get():  # Check if paused
                self.dfs_util(neighbor, search_node, visited, path_cost + weight, path)

    def reset_target_found(self):
        self.target_found = False

    def dfs_traversal(self):
        self.reset_colors()
        self.reset_queue_size()
        self.reset_target_found()  # Reset the target_found variable
        start_node = self.start_node_entry.get()
        search_node = self.search_node_entry.get()
        visited = set()

        # Pass 0 as the initial path cost and an empty path
        self.dfs_util(start_node, search_node, visited, 0, [])

        if not self.target_found:
            self.status_label.config(
                text=f"All nodes are already visited and Node {search_node} is not found")
        self.dfs_running = False

    def hill_climbing(self):
        self.reset_colors()
        self.reset_queue_size()
        start_node = self.start_node_entry.get()
        search_node = self.search_node_entry.get()
        current_node = start_node
        total_cost = 0
        path = [current_node]
        visited = set([start_node])

        while current_node != search_node and not self.pause_var.get():
            neighbors = [(neighbor, weight) for neighbor, weight in graph.graph[current_node].items() if neighbor not in visited]
            if not neighbors:
                break  # No unvisited neighbors, stop climbing

            # Choose the neighbor with the highest weight (assuming maximization problem)
            next_node, weight = min(neighbors, key=lambda x: x[1])

            total_cost += weight  # Accumulate the total cost
            path.append(next_node)  # Extend the current path
            self.update_node_color(current_node, 'green')  # Mark as visited
            self.draw_edge(current_node, next_node, weight)
            self.status_label.config(text=f"Moving from {current_node} to {next_node}, Path: {path}, Total Cost: {total_cost}")
            self.master.update()
            time.sleep(1 / self.speed_var.get())  # Adjust speed

            visited.add(next_node)
            current_node = next_node
        
        self.update_node_color(current_node, 'green')
        if current_node == search_node:
            self.status_label.config(
                text=f"Node {search_node} found! Path: {path}, Total Cost: {total_cost}")
        else:
            self.status_label.config(
                text=f"Hill climbing stopped. Node {search_node} not found! Total cost: {total_cost}")

        self.hill_climbing_running = False

    def beam_search(self):
        self.reset_colors()
        self.reset_queue_size()
        start_node = self.start_node_entry.get()
        search_node = self.search_node_entry.get()
        beam_width = 2  # You can adjust this value as needed
        visited = set([start_node])
        
        beam = [(start_node, 0, [start_node])]  # Each beam item is a tuple (node, total_cost, path)

        while beam and not self.pause_var.get():
            next_beam = []
            for current_node, total_cost, path in beam:
                neighbors = [(neighbor, weight) for neighbor, weight in graph.graph[current_node].items() if neighbor not in visited]
                for neighbor, weight in neighbors:
                    new_total_cost = total_cost + weight  # Accumulate the total cost
                    new_path = path + [neighbor]  # Extend the current path
                    next_beam.append((neighbor, new_total_cost, new_path))

            # Select the top-k items from the next beam
            next_beam = sorted(next_beam, key=lambda x: x[1])[:beam_width]

            for current_node, total_cost, path in next_beam:
                self.update_node_color(current_node, 'green')  # Mark as visited
                self.status_label.config(text=f"Visiting node {current_node}, Path: {path}, Total Cost: {total_cost}")
                self.master.update()
                time.sleep(1 / self.speed_var.get())  # Adjust speed
                visited.add(current_node)

                if current_node == search_node:
                    self.status_label.config(
                        text=f"Node {search_node} found! Path: {path}, Total Cost: {total_cost}")
                    self.beam_search_running = False
                    return  # Stop the search if the node is found

            beam = next_beam

        self.status_label.config(
            text=f"Beam search stopped. Node {search_node} not found! Total Cost: {total_cost}")
        self.beam_search_running = False

root = tk.Tk()
app = PathSearchingApp(root)
root.mainloop()

