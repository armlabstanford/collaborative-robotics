#include <cstdio>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include "rclcpp_action/rclcpp_action.hpp"
#include "locobot_wrapper_msgs/action/move_arm.hpp"
#include <moveit/move_group_interface/move_group_interface.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>


class MoveArmActionServer : public rclcpp::Node
{
public:
  using ActionMoveArm = locobot_wrapper_msgs::action::MoveArm;
  using GoalHandle = rclcpp_action::ServerGoalHandle<ActionMoveArm>;
  using MoveitGroupInterface = moveit::planning_interface::MoveGroupInterface;

  explicit MoveArmActionServer(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
  : Node("action_server_node", options)
  {
      using namespace std::placeholders;
      printf("Server Started!\n");

      // declare test parameter
      this->declare_parameter("robot_description", "");
      this->declare_parameter("robot_description_semantic", "");

      this->action_server_ = rclcpp_action::create_server<ActionMoveArm>(
        this,
        "movearm",
        std::bind(&MoveArmActionServer::handle_goal, this, _1, _2),
        std::bind(&MoveArmActionServer::handle_cancel, this, _1),
        std::bind(&MoveArmActionServer::handle_accepted, this, _1)
      );
      
      // Create the move group node
      move_group_node = std::make_shared<rclcpp::Node>(
        "locobot_moveit",
        rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true)
      );    

  }

private:
  rclcpp_action::Server<ActionMoveArm>::SharedPtr action_server_;
  std::shared_ptr<rclcpp::Node> move_group_node;

  rclcpp_action::GoalResponse handle_goal(
      const rclcpp_action::GoalUUID & uuid,
      std::shared_ptr<const ActionMoveArm::Goal> goal)
  {
      RCLCPP_INFO(this->get_logger(), "Received goal request");
      (void)uuid;
      return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  rclcpp_action::CancelResponse handle_cancel(
      const std::shared_ptr<GoalHandle> goal_handle)
  {
      RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");
      (void)goal_handle;
      return rclcpp_action::CancelResponse::ACCEPT;
  }

  void handle_accepted(const std::shared_ptr<GoalHandle> goal_handle)
  {
      using namespace std::placeholders;
      // this needs to return quickly to avoid blocking the executor, so spin up a new thread
      std::thread{std::bind(&MoveArmActionServer::execute, this, _1), goal_handle}.detach();
  }

  void execute(const std::shared_ptr<GoalHandle> goal_handle)
  {

    // print value of parameter
    RCLCPP_INFO(this->get_logger(), "Executing goal");

    rclcpp::Rate loop_rate(1);
    auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<ActionMoveArm::Feedback>();
    auto result = std::make_shared<ActionMoveArm::Result>();

    // Create a ROS logger
    auto const logger = rclcpp::get_logger("locobot_moveit");

    // create the moveit options
    moveit::planning_interface::MoveGroupInterface::Options toptions("interbotix_arm", "robot_description");

    // Create the MoveIt MoveGroup Interface
    using moveit::planning_interface::MoveGroupInterface;
    RCLCPP_INFO(this->get_logger(), "Created MoveGroupInterface");
    auto move_group_interface = MoveGroupInterface(this->move_group_node, toptions);


    // Set a target Pose
    geometry_msgs::msg::Pose target_pose;

    //position 
    target_pose.position.x = goal->pose[0];
    target_pose.position.y = goal->pose[1];
    target_pose.position.z = goal->pose[2];

    // orientation
    tf2::Quaternion q;
    float roll = (3.14159/180)*goal->pose[3];
    float pitch = (3.14159/180)*goal->pose[4];
    float yaw = (3.14159/180)*goal->pose[5];
    q.setRPY(roll, pitch, yaw);
    target_pose.orientation = tf2::toMsg(q);
    move_group_interface.setPoseTarget(target_pose);

    // Create a plan to that target pose
    auto const [plan_success, plan] = [&move_group_interface]{
      moveit::planning_interface::MoveGroupInterface::Plan msg;
      auto const ok = static_cast<bool>(move_group_interface.plan(msg));
      return std::make_pair(ok, msg);
    }();

    // Execute the plan
    if(!plan_success) {
      result->success = false;
      RCLCPP_ERROR(logger, "Planning failed!");
    } else {
      result->success = true;
      move_group_interface.execute(plan);
    }
    goal_handle->succeed(result);
  }
};  // class MoveArmActionServer


int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);

  auto action_server = std::make_shared<MoveArmActionServer>();
  rclcpp::spin(action_server);

  rclcpp::shutdown();
  return 0;
}