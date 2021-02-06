#include <ros/ros.h>
#include <geometry_msgs/Point.h>
#include <ds/Direction.h>
#include <std_msgs/Bool.h>
class directionMessageClass
{
public:
    ds::Direction dirc;
    void directionMessageCallback (const  ds::Direction &msg);
};

class poseMessageClass
{
public:
    geometry_msgs::Point pose;
    void poseMesssageCallback (const geometry_msgs::Point &msg);
};
class goalMessageClass
{
public:
    std_msgs::Bool goal;
    void goalMessageCallback (const std_msgs::Bool &msg);
};
void poseMessageClass :: poseMesssageCallback (const geometry_msgs::Point &msg)
{
    pose = msg;
}

void directionMessageClass ::directionMessageCallback(const ds::Direction &msg)
{
    dirc = msg;
}
void goalMessageClass ::goalMessageCallback(const std_msgs::Bool &msg)
{
    goal = msg;
}
geometry_msgs:: Point forward(int front, geometry_msgs::Point &pose)
{
    geometry_msgs:: Point target;
    if (front == 0)
    {
        target.x = pose.x;
        target.y = pose.y - 1;
    }
    if (front == 1)
    {
        target.x = pose.x;
        target.y = pose.y + 1;
    }
    if (front == 2)
    {
        target.x = pose.x - 1;
        target.y = pose.y;
    }
    if (front == 3)
    {
        target.x = pose.x + 1;
        target.y = pose.y ;
    }
    return target;
}
void turnVec(int &vector)
{
    if(vector == 0){
        vector = 2;
        return;
    }
    if(vector == 1){
        vector = 3;
        return;
    }

    if(vector==2){
        vector = 1;
        return;
    }
    if(vector == 3){
        vector = 0;
        return;
    }

}
void turnLeft(int &left,int &front)
{
    turnVec(left);
    turnVec(front);
}

int opposite(int &left)
{
    if(left == 0)
        return 1;
    if(left == 1)
        return 0;
    if(left == 2)
        return 3;
    if(left == 3)
        return 2;
}

void followWall(int &left, int &front,ds::Direction dirc ,geometry_msgs:: Point &pose,geometry_msgs::Point &target)
{

    if( dirc.direction[left] == false && dirc.direction[front] == true)
    {
        target = forward(front,pose);
        return;

    }
    if (dirc.direction[left ] == true && dirc.direction[front] == false)
    {
        turnLeft(left,front);
        target = forward(front,pose);
        return;
    }
    if (dirc.direction[left ] == true && dirc.direction[front] == true)
    {
        turnLeft(left,front);
        target = forward(front,pose);
        return;
    }
    if(dirc.direction[left] == false && dirc.direction[front] == false)
    {
        if(dirc.direction[opposite(left)] == true)
        {
            int temp;
            temp = front;
            front = opposite(left);
            left = temp;
            target = forward(front,pose);
            return;
        } else
        {
            turnLeft(left,front);
            turnLeft(left,front);
        }

        return;
    }
}

class stack{
public:
    int stk[256][2] ;
    int stp;
    stack()
    {
        stp = 0;
    }
    bool searchStack(int x, int y)
    {
        for(int i = stp ; i >= 0 ; i--)
        {
            if (stk[i][0] == x)
            {
                if(stk[i][1] == y)
                {
                    return true;
                }
            }
        }
        return false;
    }
    void popStk(int x, int y)
    {
        int i = stp;
        while(stk[i][0] != x && stk[i][1] != y)
        {
            stk[i][0] = NULL;
            stk[i][1] = NULL;
            i -= 1;
            std::cout<<"galti2"<<std::endl;
        }
    }
    void  pushStk(int x, int y)
    {
        stp += 1;
        stk[stp][0] = x;
        stk[stp][1] = y;
    }
    void printStk()
    {
        for (int i = stp; i >= 0 ; i--)
        {
            std::cout<< "( " << stk[i][0] << " , " << stk[i][1] << " )" ;
        }
        std::cout<<std::endl;
    }
};
int main(int argc, char **argv) {
    stack st1;
    ros::init(argc, argv, "solver");
    ros::NodeHandle nh;
    geometry_msgs::Point target;
    poseMessageClass poseMessage;
    directionMessageClass directionMessage;
    goalMessageClass goalMessage;
    ros::Subscriber subPose = nh.subscribe("pose", 1000, &poseMessageClass::poseMesssageCallback, &poseMessage);
    ros::Subscriber subDir = nh.subscribe("walls", 1000, &directionMessageClass::directionMessageCallback,
                                          &directionMessage);
    ros::Subscriber subGoal = nh.subscribe("goal", 1000, &goalMessageClass::goalMessageCallback, &goalMessage);
    ros::Publisher pubTarget = nh.advertise<geometry_msgs::Point>("target", 1000);
    ros::Rate rate(3);
    int left = 0;
    int front = 3;
    int goal[2];
    goal[0] = 2;
    goal[1] = 2;
    while (ros::ok()) {
        ros::spinOnce();
        followWall(left, front, directionMessage.dirc, poseMessage.pose, target);
        pubTarget.publish(target);
        while ((poseMessage.pose.x != target.x) && (poseMessage.pose.y != target.y)) {
            pubTarget.publish(target);
            ros::spinOnce();
            std::cout << "galti1" << std::endl;
        }
        if(st1.searchStack(poseMessage.pose.x,poseMessage.pose.y))
        {
            st1.popStk(poseMessage.pose.x, poseMessage.pose.y);
        } else
        {
            st1.pushStk(poseMessage.pose.x, poseMessage.pose.y);
        }
        ROS_INFO_STREAM("front = " << front << " target = " << target.x << " " << target.y << "\n");

        if (goal[0] == poseMessage.pose.x && goal[1] == poseMessage.pose.y) {
            st1.printStk();
            break;
        }
        rate.sleep();

    }
}
